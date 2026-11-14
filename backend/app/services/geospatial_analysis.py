"""
Geospatial Analysis Service
Calculations for vegetation indices, terrain analysis, and spatial processing.
"""
import math
from datetime import date, datetime
from typing import Optional, Dict, Any, List, Tuple
from dataclasses import dataclass
import numpy as np


@dataclass
class VegetationIndexResult:
    """Result of vegetation index calculation"""
    index_name: str
    value: float
    interpretation: str
    date: str
    quality: str  # good, fair, poor
    metadata: Dict[str, Any] = None


@dataclass
class TimeSeriesPoint:
    """Single point in a time series"""
    date: str
    value: float
    quality: str
    metadata: Dict[str, Any] = None


@dataclass
class NDVITimeSeries:
    """NDVI time series for a location"""
    latitude: float
    longitude: float
    points: List[TimeSeriesPoint]
    statistics: Dict[str, Any] = None


class GeospatialAnalysisService:
    """
    Service for geospatial and vegetation analysis calculations.

    Includes:
    - Vegetation indices (NDVI, EVI, SAVI, etc.)
    - Time series analysis (trends, anomalies, phenology)
    - Terrain analysis (slope, aspect, elevation)
    - Zonal statistics
    """

    def __init__(self):
        pass

    # ========================================================================
    # VEGETATION INDICES
    # ========================================================================

    def calculate_ndvi(self, nir: float, red: float) -> float:
        """
        Calculate NDVI (Normalized Difference Vegetation Index)

        NDVI = (NIR - Red) / (NIR + Red)
        Range: -1 to 1
        """
        if nir + red == 0:
            return 0.0
        return (nir - red) / (nir + red)

    def calculate_evi(self, nir: float, red: float, blue: float,
                      L: float = 1.0, C1: float = 6.0, C2: float = 7.5, G: float = 2.5) -> float:
        """
        Calculate EVI (Enhanced Vegetation Index)

        EVI = G * (NIR - Red) / (NIR + C1*Red - C2*Blue + L)
        Less sensitive to soil and atmospheric effects than NDVI
        """
        denominator = nir + C1 * red - C2 * blue + L
        if denominator == 0:
            return 0.0
        return G * (nir - red) / denominator

    def calculate_savi(self, nir: float, red: float, L: float = 0.5) -> float:
        """
        Calculate SAVI (Soil Adjusted Vegetation Index)

        SAVI = (NIR - Red) / (NIR + Red + L) * (1 + L)
        L=0.5 for intermediate vegetation cover
        """
        denominator = nir + red + L
        if denominator == 0:
            return 0.0
        return (nir - red) / denominator * (1 + L)

    def calculate_msavi(self, nir: float, red: float) -> float:
        """
        Calculate MSAVI2 (Modified Soil Adjusted Vegetation Index 2)

        Self-adjusting L parameter
        """
        # MSAVI2 = (2*NIR + 1 - sqrt((2*NIR + 1)^2 - 8*(NIR - Red))) / 2
        term = 2 * nir + 1
        discriminant = term * term - 8 * (nir - red)
        if discriminant < 0:
            return 0.0
        return (term - math.sqrt(discriminant)) / 2

    def calculate_ndwi(self, nir: float, swir: float) -> float:
        """
        Calculate NDWI (Normalized Difference Water Index)

        NDWI = (NIR - SWIR) / (NIR + SWIR)
        Sensitive to vegetation water content
        """
        if nir + swir == 0:
            return 0.0
        return (nir - swir) / (nir + swir)

    def calculate_ndmi(self, nir: float, swir: float) -> float:
        """
        Calculate NDMI (Normalized Difference Moisture Index)

        NDMI = (NIR - SWIR) / (NIR + SWIR) - same formula as NDWI
        """
        return self.calculate_ndwi(nir, swir)

    def calculate_gndvi(self, nir: float, green: float) -> float:
        """
        Calculate GNDVI (Green NDVI)

        GNDVI = (NIR - Green) / (NIR + Green)
        More sensitive to chlorophyll
        """
        if nir + green == 0:
            return 0.0
        return (nir - green) / (nir + green)

    def calculate_all_indices(self, bands: Dict[str, float]) -> Dict[str, float]:
        """Calculate all available vegetation indices from band values"""
        indices = {}

        # Required: NIR, Red
        nir = bands.get("nir", bands.get("B8", bands.get("B5", 0)))
        red = bands.get("red", bands.get("B4", bands.get("B4", 0)))

        if nir and red:
            indices["ndvi"] = self.calculate_ndvi(nir, red)
            indices["savi"] = self.calculate_savi(nir, red)
            indices["msavi"] = self.calculate_msavi(nir, red)

        # EVI needs Blue
        blue = bands.get("blue", bands.get("B2", bands.get("B1", 0)))
        if nir and red and blue:
            indices["evi"] = self.calculate_evi(nir, red, blue)

        # NDWI/NDMI need SWIR
        swir = bands.get("swir", bands.get("B11", bands.get("B6", 0)))
        if nir and swir:
            indices["ndwi"] = self.calculate_ndwi(nir, swir)
            indices["ndmi"] = self.calculate_ndmi(nir, swir)

        # GNDVI needs Green
        green = bands.get("green", bands.get("B3", bands.get("B2", 0)))
        if nir and green:
            indices["gndvi"] = self.calculate_gndvi(nir, green)

        return indices

    def interpret_ndvi(self, ndvi: float) -> Dict[str, str]:
        """Interpret NDVI value"""
        if ndvi < 0:
            return {"class": "water_snow_cloud", "description": "Water, snow, or clouds"}
        elif ndvi < 0.1:
            return {"class": "bare_soil", "description": "Bare soil or very sparse vegetation"}
        elif ndvi < 0.2:
            return {"class": "very_low", "description": "Very low vegetation (rock, sand)"}
        elif ndvi < 0.3:
            return {"class": "low", "description": "Low vegetation (grassland, crops early stage)"}
        elif ndvi < 0.4:
            return {"class": "moderate", "description": "Moderate vegetation (crops mid-season)"}
        elif ndvi < 0.6:
            return {"class": "high", "description": "High vegetation (dense crops, forest)"}
        else:
            return {"class": "very_high", "description": "Very high vegetation (dense forest)"}

    # ========================================================================
    # TIME SERIES ANALYSIS
    # ========================================================================

    def create_ndvi_time_series(self, latitude: float, longitude: float,
                                observations: List[Dict[str, Any]]) -> NDVITimeSeries:
        """
        Create NDVI time series from satellite observations.

        observations: List of dicts with date, ndvi, cloud_cover, etc.
        """
        points = []
        for obs in observations:
            ndvi = obs.get("ndvi")
            if ndvi is None:
                continue

            quality = "good"
            cloud = obs.get("cloud_cover", 0)
            if cloud > 20:
                quality = "fair"
            if cloud > 50:
                quality = "poor"

            points.append(TimeSeriesPoint(
                date=obs.get("date", ""),
                value=float(ndvi),
                quality=quality,
                metadata={
                    "cloud_cover": cloud,
                    "sensor": obs.get("sensor", "unknown"),
                    "interpretation": self.interpret_ndvi(float(ndvi))["description"]
                }
            ))

        # Sort by date
        points.sort(key=lambda p: p.date)

        # Calculate statistics
        stats = self._calculate_time_series_stats(points)

        return NDVITimeSeries(
            latitude=latitude,
            longitude=longitude,
            points=points,
            statistics=stats
        )

    def _calculate_time_series_stats(self, points: List[TimeSeriesPoint]) -> Dict[str, Any]:
        """Calculate statistics for NDVI time series"""
        if not points:
            return {}

        values = [p.value for p in points]
        dates = [datetime.fromisoformat(p.date).date() for p in points if p.date]

        stats = {
            "count": len(values),
            "mean": float(np.mean(values)),
            "std": float(np.std(values)),
            "min": float(np.min(values)),
            "max": float(np.max(values)),
            "median": float(np.median(values)),
        }

        if dates:
            stats["date_range"] = {
                "start": min(dates).isoformat(),
                "end": max(dates).isoformat(),
                "span_days": (max(dates) - min(dates)).days
            }

        # Trend (simple linear regression)
        if len(values) > 2:
            x = np.arange(len(values))
            y = np.array(values)
            slope, intercept = np.polyfit(x, y, 1)
            stats["trend"] = {
                "slope": float(slope),
                "direction": "increasing" if slope > 0.001 else "decreasing" if slope < -0.001 else "stable",
                "r_squared": float(np.corrcoef(x, y)[0, 1] ** 2) if len(values) > 1 else 0
            }

        # Seasonal metrics (if enough data)
        if len(values) >= 12:
            stats["seasonal"] = self._calculate_seasonal_metrics(points)

        return stats

    def _calculate_seasonal_metrics(self, points: List[TimeSeriesPoint]) -> Dict[str, Any]:
        """Calculate seasonal metrics from time series"""
        # Group by month
        monthly = {}
        for p in points:
            try:
                d = datetime.fromisoformat(p.date).date()
                month = d.month
                if month not in monthly:
                    monthly[month] = []
                monthly[month].append(p.value)
            except:
                continue

        monthly_avg = {m: float(np.mean(vals)) for m, vals in monthly.items() if vals}

        if not monthly_avg:
            return {}

        # Find peak vegetation month
        peak_month = max(monthly_avg, key=monthly_avg.get)
        min_month = min(monthly_avg, key=monthly_avg.get)

        return {
            "monthly_averages": monthly_avg,
            "peak_month": peak_month,
            "peak_value": monthly_avg[peak_month],
            "minimum_month": min_month,
            "minimum_value": monthly_avg[min_month],
            "amplitude": monthly_avg[peak_month] - monthly_avg[min_month]
        }

    def detect_anomalies(self, points: List[TimeSeriesPoint],
                        threshold: float = 2.0) -> List[Dict[str, Any]]:
        """
        Detect anomalies in NDVI time series using z-score.

        Returns list of anomalous points.
        """
        if len(points) < 3:
            return []

        values = np.array([p.value for p in points])
        mean = np.mean(values)
        std = np.std(values)

        if std == 0:
            return []

        anomalies = []
        for i, p in enumerate(points):
            z_score = abs((p.value - mean) / std)
            if z_score > threshold:
                anomalies.append({
                    "date": p.date,
                    "value": p.value,
                    "z_score": float(z_score),
                    "expected_range": [float(mean - threshold * std), float(mean + threshold * std)],
                    "type": "high" if p.value > mean else "low"
                })

        return anomalies

    def calculate_phenology(self, points: List[TimeSeriesPoint]) -> Dict[str, Any]:
        """
        Calculate phenological metrics from NDVI time series.

        Uses threshold-based method for start/end of season.
        """
        if len(points) < 10:
            return {"error": "Insufficient data for phenology analysis"}

        # Smooth the time series (simple moving average)
        values = [p.value for p in points]
        dates = [datetime.fromisoformat(p.date).date() for p in points]

        window = 3
        smoothed = []
        for i in range(len(values)):
            start = max(0, i - window // 2)
            end = min(len(values), i + window // 2 + 1)
            smoothed.append(np.mean(values[start:end]))

        # Calculate annual amplitude
        annual_min = np.min(smoothed)
        annual_max = np.max(smoothed)
        amplitude = annual_max - annual_min

        if amplitude < 0.1:
            return {"error": "Low seasonality amplitude"}

        # Threshold method: 20% and 50% of amplitude
        threshold_20 = annual_min + 0.2 * amplitude
        threshold_50 = annual_min + 0.5 * amplitude

        # Find SOS (Start of Season) - first crossing of 20% threshold upward
        sos_idx = None
        for i in range(1, len(smoothed)):
            if smoothed[i-1] < threshold_20 and smoothed[i] >= threshold_20:
                sos_idx = i
                break

        # Find EOS (End of Season) - last crossing of 20% threshold downward
        eos_idx = None
        for i in range(len(smoothed)-2, -1, -1):
            if smoothed[i] >= threshold_20 and smoothed[i+1] < threshold_20:
                eos_idx = i
                break

        # Find peak
        peak_idx = np.argmax(smoothed)

        result = {
            "amplitude": float(amplitude),
            "annual_min": float(annual_min),
            "annual_max": float(annual_max),
            "threshold_20": float(threshold_20),
            "threshold_50": float(threshold_50),
        }

        if sos_idx is not None:
            result["start_of_season"] = {
                "date": dates[sos_idx].isoformat(),
                "ndvi": float(smoothed[sos_idx]),
                "day_of_year": dates[sos_idx].timetuple().tm_yday
            }

        if eos_idx is not None:
            result["end_of_season"] = {
                "date": dates[eos_idx].isoformat(),
                "ndvi": float(smoothed[eos_idx]),
                "day_of_year": dates[eos_idx].timetuple().tm_yday
            }

        if peak_idx is not None:
            result["peak"] = {
                "date": dates[peak_idx].isoformat(),
                "ndvi": float(smoothed[peak_idx]),
                "day_of_year": dates[peak_idx].timetuple().tm_yday
            }

        if sos_idx is not None and eos_idx is not None:
            result["growing_season_length"] = (dates[eos_idx] - dates[sos_idx]).days

        return result

    # ========================================================================
    # TERRAIN ANALYSIS
    # ========================================================================

    def calculate_slope_aspect(self, dem: np.ndarray, cell_size: float = 30.0) -> Tuple[np.ndarray, np.ndarray]:
        """
        Calculate slope and aspect from DEM.

        Args:
            dem: 2D array of elevation values
            cell_size: Cell size in meters (default 30m for SRTM)

        Returns:
            slope (degrees), aspect (degrees 0-360)
        """
        # Horn's method for slope/aspect
        rows, cols = dem.shape
        slope = np.zeros_like(dem)
        aspect = np.zeros_like(dem)

        for i in range(1, rows - 1):
            for j in range(1, cols - 1):
                # 3x3 window
                z = dem[i-1:i+2, j-1:j+2]

                # dzdx, dzdy using Horn's method
                dzdx = ((z[0,2] + 2*z[1,2] + z[2,2]) - (z[0,0] + 2*z[1,0] + z[2,0])) / (8 * cell_size)
                dzdy = ((z[2,0] + 2*z[2,1] + z[2,2]) - (z[0,0] + 2*z[0,1] + z[0,2])) / (8 * cell_size)

                # Slope in degrees
                slope[i,j] = math.degrees(math.atan(math.sqrt(dzdx**2 + dzdy**2)))

                # Aspect in degrees (0=N, 90=E, 180=S, 270=W)
                if dzdx == 0 and dzdy == 0:
                    aspect[i,j] = -1  # flat
                else:
                    aspect_rad = math.atan2(dzdx, -dzdy)
                    aspect_deg = math.degrees(aspect_rad)
                    if aspect_deg < 0:
                        aspect_deg += 360
                    aspect[i,j] = aspect_deg

        return slope, aspect

    def calculate_twi(self, dem: np.ndarray, cell_size: float = 30.0) -> np.ndarray:
        """
        Calculate Topographic Wetness Index (TWI).

        TWI = ln(As / tan(β))
        As = specific catchment area (approximated)
        β = slope in radians
        """
        slope, _ = self.calculate_slope_aspect(dem, cell_size)

        # Simplified: use flow accumulation approximation
        # For production, use proper flow routing (D8, D-infinity)
        rows, cols = dem.shape
        twi = np.zeros_like(dem)

        for i in range(1, rows - 1):
            for j in range(1, cols - 1):
                s = math.radians(slope[i,j])
                if s > 0:
                    # Approximate specific catchment area
                    as_val = cell_size * cell_size  # very rough approximation
                    twi[i,j] = math.log(as_val / math.tan(s)) if math.tan(s) > 0 else 0

        return twi

    # ========================================================================
    # ZONAL STATISTICS
    # ========================================================================

    def zonal_statistics(self, raster: np.ndarray, zones: np.ndarray) -> Dict[int, Dict[str, float]]:
        """
        Calculate zonal statistics for raster values within zones.

        Args:
            raster: 2D array of values
            zones: 2D array of zone IDs (same shape)

        Returns:
            Dict mapping zone_id to statistics dict
        """
        stats = {}
        unique_zones = np.unique(zones)

        for zone_id in unique_zones:
            if zone_id == 0:  # Skip background
                continue

            mask = zones == zone_id
            values = raster[mask]

            if len(values) == 0:
                continue

            stats[int(zone_id)] = {
                "count": int(len(values)),
                "mean": float(np.mean(values)),
                "std": float(np.std(values)),
                "min": float(np.min(values)),
                "max": float(np.max(values)),
                "median": float(np.median(values)),
                "sum": float(np.sum(values)),
            }

        return stats

    # ========================================================================
    # DISTANCE AND AREA CALCULATIONS
    # ========================================================================

    def haversine_distance(self, lat1: float, lon1: float, lat2: float, lon2: float) -> float:
        """Calculate distance between two points in kilometers"""
        R = 6371  # Earth radius in km

        lat1_rad = math.radians(lat1)
        lat2_rad = math.radians(lat2)
        dlat = math.radians(lat2 - lat1)
        dlon = math.radians(lon2 - lon1)

        a = (math.sin(dlat/2)**2 +
             math.cos(lat1_rad) * math.cos(lat2_rad) * math.sin(dlon/2)**2)
        c = 2 * math.atan2(math.sqrt(a), math.sqrt(1-a))

        return R * c

    def polygon_area_hectares(self, coordinates: List[List[float]]) -> float:
        """
        Calculate polygon area in hectares using shoelace formula.

        coordinates: [[lon, lat], [lon, lat], ...] - closed ring
        """
        if len(coordinates) < 3:
            return 0.0

        # Ensure closed
        if coordinates[0] != coordinates[-1]:
            coordinates = coordinates + [coordinates[0]]

        # Shoelace formula (approximate for lat/lon)
        # Convert to approximate meters at centroid
        lons = [c[0] for c in coordinates]
        lats = [c[1] for c in coordinates]
        centroid_lat = np.mean(lats)

        # Meters per degree at this latitude
        m_per_deg_lat = 111320
        m_per_deg_lon = 111320 * math.cos(math.radians(centroid_lat))

        area_m2 = 0
        for i in range(len(coordinates) - 1):
            x1 = lons[i] * m_per_deg_lon
            y1 = lats[i] * m_per_deg_lat
            x2 = lons[i+1] * m_per_deg_lon
            y2 = lats[i+1] * m_per_deg_lat
            area_m2 += x1 * y2 - x2 * y1

        area_m2 = abs(area_m2) / 2
        return area_m2 / 10000  # Convert to hectares

    def point_in_polygon(self, lat: float, lon: float, polygon: List[List[float]]) -> bool:
        """Ray casting algorithm for point in polygon test"""
        x, y = lon, lat
        inside = False

        n = len(polygon)
        for i in range(n):
            j = (i + 1) % n
            xi, yi = polygon[i][0], polygon[i][1]
            xj, yj = polygon[j][0], polygon[j][1]

            if ((yi > y) != (yj > y)) and (x < (xj - xi) * (y - yi) / (yj - yi) + xi):
                inside = not inside

        return inside


# Singleton
_geospatial_service = None

def get_geospatial_analysis_service() -> GeospatialAnalysisService:
    global _geospatial_service
    if _geospatial_service is None:
        _geospatial_service = GeospatialAnalysisService()
    return _geospatial_service