from fastapi import APIRouter, HTTPException, Query
from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import date
from uuid import uuid4

router = APIRouter()


class NDVIPoint(BaseModel):
    date: str
    ndvi: float
    cloud_cover: float
    source: str  # "Sentinel-2" or "Landsat"
    quality: str  # "good", "fair", "poor"


class NDVIResponse(BaseModel):
    latitude: float
    longitude: float
    geometry: Optional[dict] = None
    data: List[NDVIPoint]
    statistics: dict


class VegetationAlert(BaseModel):
    type: str
    severity: str
    message: str
    date: str
    confidence: int


# Mock data for MVP - replace with actual Sentinel Hub / Google Earth Engine integration
def generate_mock_ndvi(lat: float, lon: float, start: date, end: date) -> List[NDVIPoint]:
    import random
    from datetime import timedelta

    data = []
    current = start
    sources = ["Sentinel-2", "Landsat"]
    while current <= end:
        # Simulate 5-day revisit for Sentinel-2
        if random.random() > 0.3:
            base_ndvi = 0.3 + 0.5 * (1 + (current.month - 6) / 6) / 2  # Seasonal pattern
            ndvi = max(0, min(1, base_ndvi + random.uniform(-0.1, 0.1)))
            cloud = random.uniform(0, 50)
            source = random.choice(sources)
            quality = "good" if cloud < 20 else "fair" if cloud < 40 else "poor"
            data.append(NDVIPoint(
                date=current.isoformat(),
                ndvi=round(ndvi, 3),
                cloud_cover=round(cloud, 1),
                source=source,
                quality=quality,
            ))
        current += timedelta(days=5)
    return data


@router.get("/ndvi", response_model=NDVIResponse)
async def get_ndvi_timeseries(
    latitude: float = Query(..., ge=-90, le=90),
    longitude: float = Query(..., ge=-180, le=180),
    start_date: Optional[date] = None,
    end_date: Optional[date] = None,
    geometry: Optional[str] = None,  # GeoJSON as string
):
    """Get NDVI time series for a location or polygon"""
    if not start_date:
        start_date = date.today().replace(year=date.today().year - 1)
    if not end_date:
        end_date = date.today()

    data = generate_mock_ndvi(latitude, longitude, start_date, end_date)

    # Calculate statistics
    ndvi_values = [d.ndvi for d in data]
    good_quality = [d for d in data if d.quality == "good"]

    stats = {
        "count": len(data),
        "good_quality_count": len(good_quality),
        "mean_ndvi": round(sum(ndvi_values) / len(ndvi_values), 3) if ndvi_values else 0,
        "min_ndvi": round(min(ndvi_values), 3) if ndvi_values else 0,
        "max_ndvi": round(max(ndvi_values), 3) if ndvi_values else 0,
        "latest_ndvi": data[-1].ndvi if data else 0,
        "latest_date": data[-1].date if data else None,
        "trend": "increasing" if len(data) > 1 and data[-1].ndvi > data[0].ndvi else "decreasing",
    }

    return NDVIResponse(
        latitude=latitude,
        longitude=longitude,
        geometry={"type": "Point", "coordinates": [longitude, latitude]} if not geometry else None,
        data=data,
        statistics=stats,
    )


@router.get("/ndvi/compare", response_model=dict)
async def compare_ndvi_periods(
    latitude: float = Query(..., ge=-90, le=90),
    longitude: float = Query(..., ge=-180, le=180),
    period1_start: date = Query(...),
    period1_end: date = Query(...),
    period2_start: date = Query(...),
    period2_end: date = Query(...),
):
    """Compare NDVI between two periods"""
    data1 = generate_mock_ndvi(latitude, longitude, period1_start, period1_end)
    data2 = generate_mock_ndvi(latitude, longitude, period2_start, period2_end)

    mean1 = sum(d.ndvi for d in data1) / len(data1) if data1 else 0
    mean2 = sum(d.ndvi for d in data2) / len(data2) if data2 else 0

    return {
        "period1": {
            "start": period1_start.isoformat(),
            "end": period1_end.isoformat(),
            "mean_ndvi": round(mean1, 3),
            "count": len(data1),
        },
        "period2": {
            "start": period2_start.isoformat(),
            "end": period2_end.isoformat(),
            "mean_ndvi": round(mean2, 3),
            "count": len(data2),
        },
        "difference": round(mean1 - mean2, 3),
        "relative_change_pct": round((mean1 - mean2) / mean2 * 100, 1) if mean2 else 0,
    }


@router.get("/alerts", response_model=List[VegetationAlert])
async def get_vegetation_alerts(
    latitude: float = Query(..., ge=-90, le=90),
    longitude: float = Query(..., ge=-180, le=180),
    days: int = Query(30, ge=1, le=365),
):
    """Get vegetation alerts for a location"""
    # Mock alerts based on NDVI analysis
    alerts = []

    # Simulate some alerts
    import random
    if random.random() > 0.7:
        alerts.append(VegetationAlert(
            type="ndvi_decline",
            severity="warning",
            message="Baisse significative du NDVI détectée sur 15% de la parcelle",
            date=date.today().isoformat(),
            confidence=82,
        ))

    if random.random() > 0.8:
        alerts.append(VegetationAlert(
            type="anomaly",
            severity="info",
            message="Zone localisée avec NDVI anormalement bas détectée",
            date=date.today().isoformat(),
            confidence=75,
        ))

    return alerts


@router.get("/sentinel/available")
async def get_sentinel_availability(
    latitude: float = Query(..., ge=-90, le=90),
    longitude: float = Query(..., ge=-180, le=180),
    start_date: Optional[date] = None,
    end_date: Optional[date] = None,
    max_cloud: float = Query(30, ge=0, le=100),
):
    """Get available Sentinel-2 images for a location"""
    if not start_date:
        start_date = date.today().replace(month=1, day=1)
    if not end_date:
        end_date = date.today()

    # Mock available dates
    import random
    from datetime import timedelta

    available = []
    current = start_date
    while current <= end_date:
        if random.random() > 0.4:  # ~60% chance of image available
            cloud = random.uniform(0, 80)
            if cloud <= max_cloud:
                available.append({
                    "date": current.isoformat(),
                    "cloud_cover": round(cloud, 1),
                    "tiles": [f"T31TCJ_{current.strftime('%Y%m%d')}"],
                    "preview_url": f"https://example.com/preview/{current.isoformat()}.jpg",
                })
        current += timedelta(days=5)

    return {
        "location": {"latitude": latitude, "longitude": longitude},
        "period": {"start": start_date.isoformat(), "end": end_date.isoformat()},
        "max_cloud_cover": max_cloud,
        "images": available,
        "total_count": len(available),
    }