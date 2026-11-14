"""
NASA POWER Connector
Source: https://power.larc.nasa.gov/api/temporal/daily/point
No API key required for basic usage.
Community: AG (Agriculture)
Parameters: T2M, T2M_MAX, T2M_MIN, PRECTOTCORR, RH2M, ALLSKY_SFC_SW_DWN, WS2M
"""
import httpx
import pandas as pd
from datetime import date, datetime
from typing import Optional, List, Dict, Any
from dataclasses import dataclass
from app.config import get_settings


@dataclass
class PowerParameters:
    """NASA POWER available parameters for agriculture"""
    TEMPERATURE = "T2M"
    TEMP_MAX = "T2M_MAX"
    TEMP_MIN = "T2M_MIN"
    PRECIPITATION = "PRECTOTCORR"
    HUMIDITY = "RH2M"
    RADIATION = "ALLSKY_SFC_SW_DWN"
    WIND_SPEED = "WS2M"

    AGRICULTURE_DEFAULT = [
        TEMPERATURE, TEMP_MAX, TEMP_MIN,
        PRECIPITATION, HUMIDITY, RADIATION, WIND_SPEED
    ]


@dataclass
class ClimateDataPoint:
    """Single day of climate data"""
    date: str
    T2M: Optional[float] = None
    T2M_MAX: Optional[float] = None
    T2M_MIN: Optional[float] = None
    PRECTOTCORR: Optional[float] = None
    RH2M: Optional[float] = None
    ALLSKY_SFC_SW_DWN: Optional[float] = None
    WS2M: Optional[float] = None


@dataclass
class PowerResponse:
    """Structured response from NASA POWER"""
    latitude: float
    longitude: float
    start_date: str
    end_date: str
    data: List[ClimateDataPoint]
    source: str = "NASA POWER"
    resolution: str = "0.5° x 0.5°"
    elevation: Optional[float] = None
    units: Dict[str, str] = None

    def __post_init__(self):
        if self.units is None:
            self.units = {
                "T2M": "°C",
                "T2M_MAX": "°C",
                "T2M_MIN": "°C",
                "PRECTOTCORR": "mm/day",
                "RH2M": "%",
                "ALLSKY_SFC_SW_DWN": "MJ/m²/day",
                "WS2M": "m/s",
            }


class NasaPowerConnector:
    """
    Connector for NASA POWER API.
    Handles authentication (none required), requests, and data parsing.
    """

    def __init__(self, timeout: int = 60):
        self.settings = get_settings()
        self.base_url = self.settings.NASA_POWER_BASE_URL
        self.timeout = timeout
        self.default_params = PowerParameters.AGRICULTURE_DEFAULT

    async def fetch(
        self,
        latitude: float,
        longitude: float,
        start_date: date,
        end_date: date,
        parameters: Optional[List[str]] = None,
        community: str = "AG"
    ) -> PowerResponse:
        """
        Fetch climate data from NASA POWER.

        Args:
            latitude: Latitude in decimal degrees (-90 to 90)
            longitude: Longitude in decimal degrees (-180 to 180)
            start_date: Start date for data retrieval
            end_date: End date for data retrieval
            parameters: List of parameter codes (default: agriculture set)
            community: Community code (default: AG)

        Returns:
            PowerResponse with structured climate data

        Raises:
            httpx.HTTPStatusError: If API returns error status
            httpx.RequestError: If request fails
        """
        params = parameters or self.default_params
        param_str = ",".join(params)

        request_params = {
            "parameters": param_str,
            "community": community,
            "latitude": latitude,
            "longitude": longitude,
            "start": start_date.strftime("%Y%m%d"),
            "end": end_date.strftime("%Y%m%d"),
            "format": "JSON",
        }

        async with httpx.AsyncClient(timeout=self.timeout) as client:
            response = await client.get(self.base_url, params=request_params)
            response.raise_for_status()
            raw_data = response.json()

        return self._parse_response(raw_data, latitude, longitude, start_date, end_date, params)

    def _parse_response(
        self,
        raw_data: Dict[str, Any],
        latitude: float,
        longitude: float,
        start_date: date,
        end_date: date,
        parameters: List[str]
    ) -> PowerResponse:
        """Parse NASA POWER JSON response into structured data"""

        if "properties" not in raw_data or "parameter" not in raw_data["properties"]:
            raise ValueError("Invalid NASA POWER response structure")

        params_data = raw_data["properties"]["parameter"]
        elevation = raw_data.get("geometry", {}).get("coordinates", [None, None, None])[2]

        # Collect all dates from all parameters
        dates = set()
        for param in parameters:
            if param in params_data:
                dates.update(params_data[param].keys())

        # Build data points
        data_points = []
        for date_str in sorted(dates):
            point = ClimateDataPoint(date=date_str)
            for param in parameters:
                if param in params_data and date_str in params_data[param]:
                    value = params_data[param][date_str]
                    # NASA POWER uses -999 as fill value
                    if value != -999 and value is not None:
                        setattr(point, param, round(value, 2))
            data_points.append(point)

        return PowerResponse(
            latitude=latitude,
            longitude=longitude,
            start_date=start_date.isoformat(),
            end_date=end_date.isoformat(),
            data=data_points,
            elevation=elevation,
        )

    async def fetch_summary(
        self,
        latitude: float,
        longitude: float,
        days: int = 365
    ) -> Dict[str, Any]:
        """Fetch and compute climate summary statistics"""
        end_date = date.today()
        start_date = date(end_date.year - 1, end_date.month, end_date.day) if days >= 365 else end_date

        response = await self.fetch(latitude, longitude, start_date, end_date)
        return self._compute_summary(response.data, f"Derniers {days} jours")

    def _compute_summary(self, data: List[ClimateDataPoint], period_label: str) -> Dict[str, Any]:
        """Compute climate summary statistics"""
        if not data:
            return {"period": period_label, "error": "No data available"}

        temps = [d.T2M for d in data if d.T2M is not None]
        tmax = [d.T2M_MAX for d in data if d.T2M_MAX is not None]
        tmin = [d.T2M_MIN for d in data if d.T2M_MIN is not None]
        precips = [d.PRECTOTCORR for d in data if d.PRECTOTCORR is not None]
        humidity = [d.RH2M for d in data if d.RH2M is not None]
        radiation = [d.ALLSKY_SFC_SW_DWN for d in data if d.ALLSKY_SFC_SW_DWN is not None]

        dry_days = sum(1 for p in precips if p < 1.0)
        hot_days = sum(1 for t in tmax if t > 30)
        frost_days = sum(1 for t in tmin if t < 0)

        return {
            "period": period_label,
            "avg_temperature": round(sum(temps) / len(temps), 1) if temps else None,
            "max_temperature": round(max(tmax), 1) if tmax else None,
            "min_temperature": round(min(tmin), 1) if tmin else None,
            "total_precipitation": round(sum(precips), 1) if precips else None,
            "avg_humidity": round(sum(humidity) / len(humidity), 1) if humidity else None,
            "total_radiation": round(sum(radiation), 1) if radiation else None,
            "dry_days": dry_days,
            "hot_days": hot_days,
            "frost_days": frost_days,
            "data_points": len(data),
        }

    async def fetch_monthly(
        self,
        latitude: float,
        longitude: float,
        year: int
    ) -> List[Dict[str, Any]]:
        """Fetch monthly summaries for a year"""
        monthly_data = []

        for month in range(1, 13):
            start = date(year, month, 1)
            if month == 12:
                end = date(year, 12, 31)
            else:
                end = date(year, month + 1, 1)
                from datetime import timedelta
                end = end - timedelta(days=1)

            try:
                response = await self.fetch(latitude, longitude, start, end)
                summary = self._compute_summary(response.data, f"{start.strftime('%B %Y')}")
                monthly_data.append(summary)
            except Exception as e:
                monthly_data.append({
                    "period": f"{start.strftime('%B %Y')}",
                    "error": str(e)
                })

        return monthly_data


# Singleton instance
_nasa_power = None

def get_nasa_power_connector() -> NasaPowerConnector:
    global _nasa_power
    if _nasa_power is None:
        _nasa_power = NasaPowerConnector()
    return _nasa_power