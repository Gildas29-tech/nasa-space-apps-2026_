from fastapi import APIRouter, HTTPException, Query
from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime, date
import httpx
import pandas as pd
from app.config import get_settings

router = APIRouter()
settings = get_settings()

# NASA POWER parameters mapping
POWER_PARAMETERS = {
    "temperature": ["T2M", "T2M_MAX", "T2M_MIN"],
    "precipitation": ["PRECTOTCORR"],
    "humidity": ["RH2M"],
    "radiation": ["ALLSKY_SFC_SW_DWN"],
    "wind": ["WS2M"],
}


class ClimateRequest(BaseModel):
    latitude: float = Field(..., ge=-90, le=90)
    longitude: float = Field(..., ge=-180, le=180)
    start_date: date
    end_date: date
    parameters: Optional[List[str]] = None


class ClimateDataPoint(BaseModel):
    date: str
    T2M: Optional[float] = None
    T2M_MAX: Optional[float] = None
    T2M_MIN: Optional[float] = None
    PRECTOTCORR: Optional[float] = None
    RH2M: Optional[float] = None
    ALLSKY_SFC_SW_DWN: Optional[float] = None
    WS2M: Optional[float] = None


class ClimateResponse(BaseModel):
    latitude: float
    longitude: float
    start_date: str
    end_date: str
    data: List[ClimateDataPoint]
    source: str = "NASA POWER"
    resolution: str = "0.5° x 0.5°"
    units: dict = {
        "T2M": "°C",
        "T2M_MAX": "°C",
        "T2M_MIN": "°C",
        "PRECTOTCORR": "mm/day",
        "RH2M": "%",
        "ALLSKY_SFC_SW_DWN": "MJ/m²/day",
        "WS2M": "m/s",
    }


class ClimateSummary(BaseModel):
    period: str
    avg_temperature: Optional[float] = None
    max_temperature: Optional[float] = None
    min_temperature: Optional[float] = None
    total_precipitation: Optional[float] = None
    avg_humidity: Optional[float] = None
    total_radiation: Optional[float] = None
    dry_days: int = 0
    hot_days: int = 0
    frost_days: int = 0


async def fetch_nasa_power(lat: float, lon: float, start: date, end: date, params: List[str]) -> dict:
    """Fetch data from NASA POWER API"""
    param_str = ",".join(params)
    url = f"{settings.NASA_POWER_BASE_URL}"
    request_params = {
        "parameters": param_str,
        "community": "AG",
        "latitude": lat,
        "longitude": lon,
        "start": start.strftime("%Y%m%d"),
        "end": end.strftime("%Y%m%d"),
        "format": "JSON",
    }

    async with httpx.AsyncClient(timeout=settings.NASA_POWER_TIMEOUT) as client:
        response = await client.get(url, params=request_params)
        response.raise_for_status()
        return response.json()


def process_nasa_power_data(raw_data: dict, parameters: List[str]) -> List[ClimateDataPoint]:
    """Process NASA POWER JSON response into structured data"""
    if "properties" not in raw_data or "parameter" not in raw_data["properties"]:
        return []

    params_data = raw_data["properties"]["parameter"]
    dates = set()
    for param in parameters:
        if param in params_data:
            dates.update(params_data[param].keys())

    result = []
    for date_str in sorted(dates):
        point = ClimateDataPoint(date=date_str)
        for param in parameters:
            if param in params_data and date_str in params_data[param]:
                value = params_data[param][date_str]
                if value != -999:  # NASA POWER fill value
                    setattr(point, param, round(value, 2))
        result.append(point)

    return result


def calculate_summary(data: List[ClimateDataPoint], period_label: str) -> ClimateSummary:
    """Calculate climate summary statistics"""
    if not data:
        return ClimateSummary(period=period_label)

    temps = [d.T2M for d in data if d.T2M is not None]
    tmax = [d.T2M_MAX for d in data if d.T2M_MAX is not None]
    tmin = [d.T2M_MIN for d in data if d.T2M_MIN is not None]
    precips = [d.PRECTOTCORR for d in data if d.PRECTOTCORR is not None]
    humidity = [d.RH2M for d in data if d.RH2M is not None]
    radiation = [d.ALLSKY_SFC_SW_DWN for d in data if d.ALLSKY_SFC_SW_DWN is not None]

    dry_days = sum(1 for p in precips if p < 1.0)
    hot_days = sum(1 for t in tmax if t > 30)
    frost_days = sum(1 for t in tmin if t < 0)

    return ClimateSummary(
        period=period_label,
        avg_temperature=round(sum(temps) / len(temps), 1) if temps else None,
        max_temperature=round(max(tmax), 1) if tmax else None,
        min_temperature=round(min(tmin), 1) if tmin else None,
        total_precipitation=round(sum(precips), 1) if precips else None,
        avg_humidity=round(sum(humidity) / len(humidity), 1) if humidity else None,
        total_radiation=round(sum(radiation), 1) if radiation else None,
        dry_days=dry_days,
        hot_days=hot_days,
        frost_days=frost_days,
    )


@router.post("/fetch", response_model=ClimateResponse)
async def fetch_climate_data(request: ClimateRequest):
    """Fetch climate data from NASA POWER"""
    params = request.parameters or [
        "T2M", "T2M_MAX", "T2M_MIN", "PRECTOTCORR", "RH2M", "ALLSKY_SFC_SW_DWN", "WS2M"
    ]

    try:
        raw_data = await fetch_nasa_power(
            request.latitude,
            request.longitude,
            request.start_date,
            request.end_date,
            params,
        )
    except httpx.HTTPStatusError as e:
        raise HTTPException(status_code=502, detail=f"Erreur NASA POWER: {e.response.status_code}")
    except httpx.RequestError as e:
        raise HTTPException(status_code=503, detail=f"Service NASA POWER indisponible: {str(e)}")

    data = process_nasa_power_data(raw_data, params)

    return ClimateResponse(
        latitude=request.latitude,
        longitude=request.longitude,
        start_date=request.start_date.isoformat(),
        end_date=request.end_date.isoformat(),
        data=data,
    )


@router.get("/summary", response_model=ClimateSummary)
async def get_climate_summary(
    latitude: float = Query(..., ge=-90, le=90),
    longitude: float = Query(..., ge=-180, le=180),
    days: int = Query(365, ge=1, le=3650),
):
    """Get climate summary for the last N days"""
    end_date = date.today()
    start_date = date(end_date.year - 1, end_date.month, end_date.day) if days >= 365 else date.today().replace(day=1)

    params = ["T2M", "T2M_MAX", "T2M_MIN", "PRECTOTCORR", "RH2M", "ALLSKY_SFC_SW_DWN", "WS2M"]

    try:
        raw_data = await fetch_nasa_power(latitude, longitude, start_date, end_date, params)
    except Exception as e:
        raise HTTPException(status_code=503, detail=f"Erreur récupération données: {str(e)}")

    data = process_nasa_power_data(raw_data, params)
    period_label = f"Derniers {days} jours" if days < 365 else f"Année {end_date.year}"

    return calculate_summary(data, period_label)


@router.get("/monthly", response_model=List[ClimateSummary])
async def get_monthly_climate(
    latitude: float = Query(..., ge=-90, le=90),
    longitude: float = Query(..., ge=-180, le=180),
    year: int = Query(..., ge=2000, le=2030),
):
    """Get monthly climate summaries for a year"""
    summaries = []
    params = ["T2M", "T2M_MAX", "T2M_MIN", "PRECTOTCORR", "RH2M", "ALLSKY_SFC_SW_DWN", "WS2M"]

    for month in range(1, 13):
        start = date(year, month, 1)
        if month == 12:
            end = date(year, 12, 31)
        else:
            end = date(year, month + 1, 1).replace(day=1) - pd.Timedelta(days=1)

        try:
            raw_data = await fetch_nasa_power(latitude, longitude, start, end, params)
            data = process_nasa_power_data(raw_data, params)
            summary = calculate_summary(data, f"{start.strftime('%B %Y')}")
            summaries.append(summary)
        except Exception:
            summaries.append(ClimateSummary(period=f"{start.strftime('%B %Y')}"))

    return summaries