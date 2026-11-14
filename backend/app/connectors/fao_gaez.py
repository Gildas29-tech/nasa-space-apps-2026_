"""
FAO GAEZ Connector
Global Agro-Ecological Zones data from FAO.
Not a traditional API - uses downloaded raster datasets.
"""
import os
import rasterio
import numpy as np
from datetime import date
from typing import Optional, List, Dict, Any, Tuple
from dataclasses import dataclass
from pathlib import Path
from app.config import get_settings


@dataclass
class GaezDataPoint:
    """GAEZ data point for a location"""
    latitude: float
    longitude: float
    suitability_index: Optional[float] = None  # 0-100 or class
    potential_yield: Optional[float] = None  # t/ha
    crop_name: Optional[str] = None
    water_supply: Optional[str] = None  # rainfed/irrigated
    input_level: Optional[str] = None  # high/medium/low
    year: Optional[int] = None


@dataclass
class GaezResponse:
    """GAEZ response"""
    latitude: float
    longitude: float
    crop_data: List[GaezDataPoint]
    source: str = "FAO GAEZ v4"
    resolution: str = "5 arc-minutes (~9km at equator)"


class FaoGaezConnector:
    """
    Connector for FAO GAEZ data.

    GAEZ is not a real-time API. It provides pre-computed raster datasets:
    - Land suitability (by crop, water supply, input level)
    - Potential yields
    - Agro-climatic indicators
    - Soil/terrain constraints

    Approach:
    1. Download required GAEZ rasters (GeoTIFF) from FAO
    2. Store locally or in cloud storage
    3. Query using rasterio for point/polygon extraction
    4. Cache results

    Data portal: https://gaez.fao.org/
    Download: https://gaez.fao.org/pages/data-portal
    """

    def __init__(self, data_dir: str = "./data/gaez"):
        self.settings = get_settings()
        self.data_dir = Path(data_dir)
        self.data_dir.mkdir(parents=True, exist_ok=True)
        self._raster_cache: Dict[str, rasterio.DatasetReader] = {}

    def _get_raster_path(self, crop: str, water_supply: str, input_level: str, indicator: str) -> Optional[Path]:
        """
        Construct path to GAEZ raster file.

        Expected naming convention (customize based on actual files):
        GAEZ_{crop}_{water_supply}_{input_level}_{indicator}.tif

        Example: GAEZ_wheat_rainfed_high_suitability.tif
        """
        filename = f"GAEZ_{crop}_{water_supply}_{input_level}_{indicator}.tif"
        return self.data_dir / filename

    def _open_raster(self, path: Path) -> Optional[rasterio.DatasetReader]:
        """Open and cache raster dataset"""
        if str(path) in self._raster_cache:
            return self._raster_cache[str(path)]

        if path.exists():
            try:
                ds = rasterio.open(path)
                self._raster_cache[str(path)] = ds
                return ds
            except Exception as e:
                print(f"Error opening raster {path}: {e}")
        return None

    def _sample_raster(self, ds: rasterio.DatasetReader, lon: float, lat: float) -> Optional[float]:
        """Sample raster value at coordinates"""
        try:
            # Convert lat/lon to pixel coordinates
            row, col = ds.index(lon, lat)
            # Read single pixel
            value = ds.read(1, window=((row, row+1), (col, col+1)))
            if value.size > 0:
                val = value[0, 0]
                # Handle nodata
                if ds.nodata is not None and val == ds.nodata:
                    return None
                return float(val)
        except Exception:
            pass
        return None

    def get_crop_suitability(
        self,
        latitude: float,
        longitude: float,
        crops: List[str],
        water_supply: str = "rainfed",
        input_level: str = "high"
    ) -> GaezResponse:
        """
        Get crop suitability indices for location.

        Args:
            latitude: Latitude in decimal degrees
            longitude: Longitude in decimal degrees
            crops: List of crop names (GAEZ codes)
            water_supply: "rainfed" or "irrigated"
            input_level: "high", "medium", "low"
        """
        crop_data = []

        for crop in crops:
            # Suitability index raster
            suit_path = self._get_raster_path(crop, water_supply, input_level, "suitability")
            yield_path = self._get_raster_path(crop, water_supply, input_level, "yield")

            suitability = None
            potential_yield = None

            if suit_path and suit_path.exists():
                ds = self._open_raster(suit_path)
                if ds:
                    suitability = self._sample_raster(ds, longitude, latitude)

            if yield_path and yield_path.exists():
                ds = self._open_raster(yield_path)
                if ds:
                    potential_yield = self._sample_raster(ds, longitude, latitude)

            crop_data.append(GaezDataPoint(
                latitude=latitude,
                longitude=longitude,
                suitability_index=suitability,
                potential_yield=potential_yield,
                crop_name=crop,
                water_supply=water_supply,
                input_level=input_level,
            ))

        return GaezResponse(
            latitude=latitude,
            longitude=longitude,
            crop_data=crop_data
        )

    def get_agro_climatic_indicators(
        self,
        latitude: float,
        longitude: float
    ) -> Dict[str, Any]:
        """Get agro-climatic indicators (growing period, frost days, etc.)"""
        indicators = {}

        indicator_files = {
            "growing_period_days": "GAEZ_growing_period_days.tif",
            "frost_free_days": "GAEZ_frost_free_days.tif",
            "temperature_sum": "GAEZ_temperature_sum.tif",
            "moisture_index": "GAEZ_moisture_index.tif",
        }

        for name, filename in indicator_files.items():
            path = self.data_dir / filename
            if path.exists():
                ds = self._open_raster(path)
                if ds:
                    value = self._sample_raster(ds, longitude, latitude)
                    if value is not None:
                        indicators[name] = value

        return indicators

    def get_soil_terrain_constraints(
        self,
        latitude: float,
        longitude: float
    ) -> Dict[str, Any]:
        """Get soil and terrain constraints"""
        constraints = {}

        constraint_files = {
            "soil_depth": "GAEZ_soil_depth.tif",
            "soil_texture": "GAEZ_soil_texture.tif",
            "soil_ph": "GAEZ_soil_ph.tif",
            "slope": "GAEZ_slope.tif",
            "terrain_constraint": "GAEZ_terrain_constraint.tif",
        }

        for name, filename in constraint_files.items():
            path = self.data_dir / filename
            if path.exists():
                ds = self._open_raster(path)
                if ds:
                    value = self._sample_raster(ds, longitude, latitude)
                    if value is not None:
                        constraints[name] = value

        return constraints

    def list_available_data(self) -> List[str]:
        """List available GAEZ raster files"""
        return [f.name for f in self.data_dir.glob("*.tif")]

    def close(self):
        """Close all cached raster datasets"""
        for ds in self._raster_cache.values():
            ds.close()
        self._raster_cache.clear()


# Singleton
_gaez = None

def get_gaez_connector(data_dir: str = "./data/gaez") -> FaoGaezConnector:
    global _gaez
    if _gaez is None:
        _gaez = FaoGaezConnector(data_dir)
    return _gaez