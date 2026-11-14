"""
Data Collection Service
Orchestrates all data source connectors for farm analysis.
"""
import asyncio
from datetime import date, datetime
from typing import Optional, Dict, Any, List
from dataclasses import dataclass, field
from enum import Enum

from app.connectors.nasa_power import get_nasa_power_connector, PowerResponse
from app.connectors.sentinel2 import get_sentinel2_connector, SentinelSearchParams, SentinelSearchResult
from app.connectors.nasa_gpm import get_gpm_connector, GPMResponse
from app.connectors.nasa_smap import get_smap_connector, SmapResponse
from app.connectors.landsat import get_landsat_connector, LandsatSearchResult
from app.connectors.fao_gaez import get_gaez_connector, GaezResponse
from app.config import get_settings


class DataSourceStatus(str, Enum):
    """Status of data source availability"""
    AVAILABLE = "available"
    PARTIAL = "partial"
    UNAVAILABLE = "unavailable"
    AUTH_ERROR = "auth_error"
    ERROR = "error"


@dataclass
class SourceResult:
    """Result from a single data source"""
    source: str
    status: DataSourceStatus
    data: Any = None
    error: Optional[str] = None
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class FarmAnalysisData:
    """Complete farm analysis data from all sources"""
    farm_id: str
    latitude: float
    longitude: float
    geometry: Optional[Dict] = None
    period_start: Optional[date] = None
    period_end: Optional[date] = None
    collected_at: datetime = field(default_factory=datetime.utcnow)

    # Source results
    climate: Optional[SourceResult] = None
    precipitation: Optional[SourceResult] = None
    soil_moisture: Optional[SourceResult] = None
    sentinel2: Optional[SourceResult] = None
    landsat: Optional[SourceResult] = None
    gaez: Optional[SourceResult] = None

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for API response"""
        result = {
            "farm_id": self.farm_id,
            "latitude": self.latitude,
            "longitude": self.longitude,
            "geometry": self.geometry,
            "period": {
                "start": self.period_start.isoformat() if self.period_start else None,
                "end": self.period_end.isoformat() if self.period_end else None,
            },
            "collected_at": self.collected_at.isoformat(),
            "sources": {}
        }

        for source_name in ["climate", "precipitation", "soil_moisture", "sentinel2", "landsat", "gaez"]:
            source_result = getattr(self, source_name)
            if source_result:
                result["sources"][source_name] = {
                    "status": source_result.status.value,
                    "data": source_result.data,
                    "error": source_result.error,
                    "metadata": source_result.metadata,
                }

        return result

    def get_available_sources(self) -> List[str]:
        """Get list of successfully collected sources"""
        available = []
        for source_name in ["climate", "precipitation", "soil_moisture", "sentinel2", "landsat", "gaez"]:
            source_result = getattr(self, source_name)
            if source_result and source_result.status == DataSourceStatus.AVAILABLE:
                available.append(source_name)
        return available

    def get_unavailable_sources(self) -> List[str]:
        """Get list of unavailable sources"""
        unavailable = []
        for source_name in ["climate", "precipitation", "soil_moisture", "sentinel2", "landsat", "gaez"]:
            source_result = getattr(self, source_name)
            if source_result and source_result.status != DataSourceStatus.AVAILABLE:
                unavailable.append(source_name)
        return unavailable


class DataCollectionService:
    """
    Service to orchestrate data collection from all sources.

    Each source is called independently - failure of one doesn't block others.
    Results include status, data, and any errors for transparency.
    """

    def __init__(self):
        self.settings = get_settings()

    async def collect_farm_data(
        self,
        farm_id: str,
        latitude: float,
        longitude: float,
        geometry: Optional[Dict] = None,
        start_date: Optional[date] = None,
        end_date: Optional[date] = None,
        include_sources: Optional[List[str]] = None
    ) -> FarmAnalysisData:
        """
        Collect data from all available sources for a farm.

        Args:
            farm_id: Unique farm identifier
            latitude: Farm latitude
            longitude: Farm longitude
            geometry: Farm polygon as GeoJSON (optional)
            start_date: Analysis period start (default: 1 year ago)
            end_date: Analysis period end (default: today)
            include_sources: Specific sources to include (default: all)

        Returns:
            FarmAnalysisData with results from all sources
        """
        if start_date is None:
            start_date = date.today().replace(year=date.today().year - 1)
        if end_date is None:
            end_date = date.today()

        if geometry is None:
            # Default to point geometry
            geometry = {
                "type": "Point",
                "coordinates": [longitude, latitude]
            }

        # Initialize result container
        result = FarmAnalysisData(
            farm_id=farm_id,
            latitude=latitude,
            longitude=longitude,
            geometry=geometry,
            period_start=start_date,
            period_end=end_date,
        )

        # Define all available sources
        all_sources = {
            "climate": self._collect_climate,
            "precipitation": self._collect_precipitation,
            "soil_moisture": self._collect_soil_moisture,
            "sentinel2": self._collect_sentinel2,
            "landsat": self._collect_landsat,
            "gaez": self._collect_gaez,
        }

        # Filter sources if specified
        sources_to_collect = all_sources
        if include_sources:
            sources_to_collect = {k: v for k, v in all_sources.items() if k in include_sources}

        # Collect all sources concurrently
        tasks = []
        for source_name, collector in sources_to_collect.items():
            tasks.append(self._safe_collect(source_name, collector, result, geometry, start_date, end_date))

        source_results = await asyncio.gather(*tasks, return_exceptions=True)

        # Assign results
        for source_name, source_result in zip(sources_to_collect.keys(), source_results):
            if isinstance(source_result, Exception):
                setattr(result, source_name, SourceResult(
                    source=source_name,
                    status=DataSourceStatus.ERROR,
                    error=str(source_result)
                ))
            else:
                setattr(result, source_name, source_result)

        return result

    async def _safe_collect(
        self,
        source_name: str,
        collector,
        result: FarmAnalysisData,
        geometry: Dict,
        start_date: date,
        end_date: date
    ) -> SourceResult:
        """Safely execute collector with error handling"""
        try:
            return await collector(geometry, start_date, end_date, result.latitude, result.longitude)
        except Exception as e:
            return SourceResult(
                source=source_name,
                status=DataSourceStatus.ERROR,
                error=f"{type(e).__name__}: {str(e)}"
            )

    async def _collect_climate(
        self,
        geometry: Dict,
        start_date: date,
        end_date: date,
        latitude: float,
        longitude: float
    ) -> SourceResult:
        """Collect climate data from NASA POWER"""
        connector = get_nasa_power_connector()
        try:
            response = await connector.fetch(latitude, longitude, start_date, end_date)
            return SourceResult(
                source="NASA POWER",
                status=DataSourceStatus.AVAILABLE,
                data=response,
                metadata={
                    "parameters": ["T2M", "T2M_MAX", "T2M_MIN", "PRECTOTCORR", "RH2M", "ALLSKY_SFC_SW_DWN", "WS2M"],
                    "resolution": response.resolution,
                    "elevation": response.elevation,
                }
            )
        except Exception as e:
            return SourceResult(
                source="NASA POWER",
                status=DataSourceStatus.UNAVAILABLE,
                error=str(e)
            )

    async def _collect_precipitation(
        self,
        geometry: Dict,
        start_date: date,
        end_date: date,
        latitude: float,
        longitude: float
    ) -> SourceResult:
        """Collect precipitation from NASA GPM IMERG"""
        connector = get_gpm_connector()
        try:
            response = await connector.fetch_daily_precipitation(latitude, longitude, start_date, end_date)
            if response.data:
                return SourceResult(
                    source="NASA GPM IMERG",
                    status=DataSourceStatus.AVAILABLE,
                    data=response,
                    metadata={"resolution": response.resolution}
                )
            else:
                return SourceResult(
                    source="NASA GPM IMERG",
                    status=DataSourceStatus.UNAVAILABLE,
                    error="GPM IMERG not fully implemented - requires Earthdata authentication"
                )
        except Exception as e:
            return SourceResult(
                source="NASA GPM IMERG",
                status=DataSourceStatus.ERROR,
                error=str(e)
            )

    async def _collect_soil_moisture(
        self,
        geometry: Dict,
        start_date: date,
        end_date: date,
        latitude: float,
        longitude: float
    ) -> SourceResult:
        """Collect soil moisture from NASA SMAP"""
        connector = get_smap_connector()
        try:
            response = await connector.fetch_soil_moisture(latitude, longitude, start_date, end_date)
            if response.data:
                return SourceResult(
                    source="NASA SMAP",
                    status=DataSourceStatus.AVAILABLE,
                    data=response,
                    metadata={"resolution": response.resolution}
                )
            else:
                return SourceResult(
                    source="NASA SMAP",
                    status=DataSourceStatus.UNAVAILABLE,
                    error="SMAP requires AppEEARS integration"
                )
        except Exception as e:
            return SourceResult(
                source="NASA SMAP",
                status=DataSourceStatus.ERROR,
                error=str(e)
            )

    async def _collect_sentinel2(
        self,
        geometry: Dict,
        start_date: date,
        end_date: date,
        latitude: float,
        longitude: float
    ) -> SourceResult:
        """Collect Sentinel-2 imagery metadata"""
        connector = get_sentinel2_connector()
        try:
            params = SentinelSearchParams(
                geometry=geometry,
                start_date=start_date,
                end_date=end_date,
                max_cloud_cover=30.0
            )
            response = await connector.search(params)

            available_dates = await connector.get_available_dates(geometry, start_date, end_date, 30.0)

            return SourceResult(
                source="Sentinel-2 (Copernicus)",
                status=DataSourceStatus.AVAILABLE if response.items else DataSourceStatus.PARTIAL,
                data={
                    "items_count": len(response.items),
                    "total_matched": response.total_matched,
                    "available_dates": available_dates[:20],  # Limit to 20
                },
                metadata={
                    "collections": params.collections,
                    "max_cloud_cover": params.max_cloud_cover,
                }
            )
        except Exception as e:
            return SourceResult(
                source="Sentinel-2",
                status=DataSourceStatus.ERROR,
                error=str(e)
            )

    async def _collect_landsat(
        self,
        geometry: Dict,
        start_date: date,
        end_date: date,
        latitude: float,
        longitude: float
    ) -> SourceResult:
        """Collect Landsat imagery metadata"""
        connector = get_landsat_connector()
        try:
            response = await connector.search(geometry, start_date, end_date, max_cloud=30.0)

            available_dates = await connector.get_available_dates(geometry, start_date, end_date, 30.0)

            return SourceResult(
                source="Landsat (USGS)",
                status=DataSourceStatus.AVAILABLE if response.items else DataSourceStatus.PARTIAL,
                data={
                    "items_count": len(response.items),
                    "total_matched": response.total_matched,
                    "available_dates": available_dates[:20],
                },
                metadata={
                    "collections": ["landsat-c2-l2"],
                }
            )
        except Exception as e:
            return SourceResult(
                source="Landsat",
                status=DataSourceStatus.ERROR,
                error=str(e)
            )

    async def _collect_gaez(
        self,
        geometry: Dict,
        start_date: date,
        end_date: date,
        latitude: float,
        longitude: float
    ) -> SourceResult:
        """Collect FAO GAEZ data"""
        connector = get_gaez_connector()
        try:
            # GAEZ crops to check (major crops)
            crops = ["wheat", "maize", "rice", "soybean", "sorghum", "sunflower", "rapeseed"]

            response = connector.get_crop_suitability(
                latitude, longitude, crops,
                water_supply="rainfed",
                input_level="high"
            )

            agro_indicators = connector.get_agro_climatic_indicators(latitude, longitude)
            soil_constraints = connector.get_soil_terrain_constraints(latitude, longitude)

            return SourceResult(
                source="FAO GAEZ",
                status=DataSourceStatus.AVAILABLE if response.crop_data else DataSourceStatus.PARTIAL,
                data={
                    "crops": [
                        {
                            "crop": cd.crop_name,
                            "suitability": cd.suitability_index,
                            "potential_yield": cd.potential_yield,
                        }
                        for cd in response.crop_data
                    ],
                    "agro_climatic": agro_indicators,
                    "soil_constraints": soil_constraints,
                },
                metadata={
                    "resolution": response.resolution,
                    "available_files": connector.list_available_data(),
                }
            )
        except Exception as e:
            return SourceResult(
                source="FAO GAEZ",
                status=DataSourceStatus.ERROR,
                error=str(e)
            )


# Singleton
_collection_service = None

def get_data_collection_service() -> DataCollectionService:
    global _collection_service
    if _collection_service is None:
        _collection_service = DataCollectionService()
    return _collection_service