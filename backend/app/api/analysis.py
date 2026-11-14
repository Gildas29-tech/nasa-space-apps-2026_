"""
Analysis API
Comprehensive farm analysis endpoints combining all services.
"""
from datetime import date, datetime
from typing import Optional, List, Dict, Any
from fastapi import APIRouter, HTTPException, Query, BackgroundTasks
from pydantic import BaseModel, Field

from app.services.data_collection import get_data_collection_service, FarmAnalysisData
from app.services.data_validation import get_data_validation_service
from app.services.geospatial_analysis import get_geospatial_analysis_service
from app.services.agricultural_analysis import get_agricultural_analysis_service
from app.api.farms import farms_db, FarmCreate, FarmResponse


router = APIRouter(tags=["analysis"])


# Request/Response models
class AnalysisRequest(BaseModel):
    """Request for farm analysis"""
    farm_id: str
    start_date: Optional[date] = None
    end_date: Optional[date] = None
    include_sources: Optional[List[str]] = None
    force_refresh: bool = False


class CropSuitabilityRequest(BaseModel):
    """Request for crop suitability analysis"""
    latitude: float
    longitude: float
    crops: Optional[List[str]] = None
    climate_data: Optional[Dict[str, Any]] = None
    soil_data: Optional[Dict[str, Any]] = None
    gaez_data: Optional[Dict[str, Any]] = None


class WaterBalanceRequest(BaseModel):
    """Request for water balance calculation"""
    crop: str
    latitude: float
    longitude: float
    start_date: date
    end_date: date
    soil_data: Optional[Dict[str, Any]] = None
    irrigation_schedule: Optional[List[Dict[str, Any]]] = None


class RotationRequest(BaseModel):
    """Request for rotation analysis"""
    current_crop: str
    proposed_crops: List[str]
    latitude: float
    longitude: float
    soil_data: Optional[Dict[str, Any]] = None
    climate_data: Optional[Dict[str, Any]] = None


class RiskAssessmentRequest(BaseModel):
    """Request for risk assessment"""
    crop: str
    latitude: float
    longitude: float
    climate_data: Optional[Dict[str, Any]] = None
    soil_data: Optional[Dict[str, Any]] = None
    ndvi_data: Optional[List[Dict[str, Any]]] = None


class YieldGapRequest(BaseModel):
    """Request for yield gap analysis"""
    crop: str
    latitude: float
    longitude: float
    climate_data: Optional[Dict[str, Any]] = None
    soil_data: Optional[Dict[str, Any]] = None
    management_level: str = "medium"


class AnalysisResponse(BaseModel):
    """Complete farm analysis response"""
    farm_id: str
    farm_name: str
    latitude: float
    longitude: float
    analysis_date: datetime
    period: Dict[str, Any]
    data_collection: Dict[str, Any]
    validation: Dict[str, Any]
    crop_suitability: List[Dict[str, Any]]
    water_balance: Optional[Dict[str, Any]] = None
    risk_assessment: List[Dict[str, Any]]
    yield_gaps: List[Dict[str, Any]]
    recommendations: List[str]


# ============================================================================
# ENDPOINTS
# ============================================================================

@router.post("/farm/{farm_id}/collect", response_model=Dict[str, Any])
async def collect_farm_data(
    farm_id: str,
    request: AnalysisRequest
):
    """
    Collect data from all sources for a farm.

    This orchestrates all connectors concurrently.
    """
    # Get farm
    if farm_id not in farms_db:
        raise HTTPException(status_code=404, detail="Farm not found")

    farm = farms_db[farm_id]

    # Parse geometry
    geometry = farm.get("geometry")
    if geometry and isinstance(geometry, str):
        import json
        geometry = json.loads(geometry)

    # Run collection
    collection_service = get_data_collection_service()
    result = await collection_service.collect_farm_data(
        farm_id=farm_id,
        latitude=farm["latitude"],
        longitude=farm["longitude"],
        geometry=geometry,
        start_date=request.start_date,
        end_date=request.end_date,
        include_sources=request.include_sources
    )

    return result.to_dict()


@router.post("/farm/{farm_id}/validate", response_model=Dict[str, Any])
async def validate_farm_data(
    farm_id: str,
    request: AnalysisRequest
):
    """
    Validate collected farm data quality.
    """
    # First collect data
    collection_service = get_data_collection_service()
    farm = farms_db.get(farm_id)

    if not farm:
        raise HTTPException(status_code=404, detail="Farm not found")

    geometry = farm.get("geometry")
    if geometry and isinstance(geometry, str):
        import json
        geometry = json.loads(geometry)

    collected = await collection_service.collect_farm_data(
        farm_id=farm_id,
        latitude=farm["latitude"],
        longitude=farm["longitude"],
        geometry=geometry,
        start_date=request.start_date,
        end_date=request.end_date,
        include_sources=request.include_sources
    )

    # Validate each source
    validation_service = get_data_validation_service()
    validation_results = {}

    source_map = {
        "climate": ("NASA POWER", validation_service.validate_nasa_power),
        "precipitation": ("NASA GPM IMERG", validation_service.validate_gpm_precipitation),
        "soil_moisture": ("NASA SMAP", validation_service.validate_smap_soil_moisture),
        "sentinel2": ("Sentinel-2", validation_service.validate_sentinel2),
        "landsat": ("Landsat", validation_service.validate_landsat),
        "gaez": ("FAO GAEZ", validation_service.validate_gaez),
    }

    start = request.start_date or date.today().replace(year=date.today().year - 1)
    end = request.end_date or date.today()

    for source_key, (source_name, validator) in source_map.items():
        source_result = getattr(collected, source_key)
        if source_result and source_result.data:
            try:
                report = validator(source_result.data, start, end)
                validation_results[source_name] = report.get_summary()
            except Exception as e:
                validation_results[source_name] = {"error": str(e)}

    # Cross-source validation
    cross_report = validation_service.validate_cross_sources(
        {k: v for k, v in validation_results.items() if "error" not in v}
    )
    validation_results["Cross-Source Validation"] = cross_report.get_summary()

    return {
        "farm_id": farm_id,
        "validation_date": datetime.utcnow().isoformat(),
        "period": {"start": start.isoformat(), "end": end.isoformat()},
        "results": validation_results
    }


@router.post("/farm/{farm_id}/complete", response_model=AnalysisResponse)
async def complete_farm_analysis(
    farm_id: str,
    request: AnalysisRequest
):
    """
    Run complete farm analysis combining all services.

    This is the main endpoint for comprehensive analysis.
    """
    farm = farms_db.get(farm_id)
    if not farm:
        raise HTTPException(status_code=404, detail="Farm not found")

    geometry = farm.get("geometry")
    if geometry and isinstance(geometry, str):
        import json
        geometry = json.loads(geometry)

    start = request.start_date or date.today().replace(year=date.today().year - 1)
    end = request.end_date or date.today()

    # 1. Collect data from all sources
    collection_service = get_data_collection_service()
    collected = await collection_service.collect_farm_data(
        farm_id=farm_id,
        latitude=farm["latitude"],
        longitude=farm["longitude"],
        geometry=geometry,
        start_date=start,
        end_date=end,
        include_sources=request.include_sources
    )

    # 2. Validate data
    validation_service = get_data_validation_service()
    validation_results = {}

    source_map = {
        "climate": ("NASA POWER", validation_service.validate_nasa_power, collected.climate),
        "precipitation": ("NASA GPM IMERG", validation_service.validate_gpm_precipitation, collected.precipitation),
        "soil_moisture": ("NASA SMAP", validation_service.validate_smap_soil_moisture, collected.soil_moisture),
        "sentinel2": ("Sentinel-2", validation_service.validate_sentinel2, collected.sentinel2),
        "landsat": ("Landsat", validation_service.validate_landsat, collected.landsat),
        "gaez": ("FAO GAEZ", validation_service.validate_gaez, collected.gaez),
    }

    for source_key, (source_name, validator, source_result) in source_map.items():
        if source_result and source_result.data:
            try:
                report = validator(source_result.data, start, end)
                validation_results[source_name] = report.get_summary()
            except Exception as e:
                validation_results[source_name] = {"error": str(e), "quality": "unusable"}

    cross_report = validation_service.validate_cross_sources(
        {k: v for k, v in validation_results.items() if "error" not in v}
    )
    validation_results["Cross-Source Validation"] = cross_report.get_summary()

    # 3. Prepare climate/soil data for agricultural analysis
    climate_data = {}
    soil_data = {}
    gaez_data = None

    if collected.climate and collected.climate.data:
        cdata = collected.climate.data
        if hasattr(cdata, 'summary'):
            climate_data = cdata.summary
        elif hasattr(cdata, 'parameters'):
            # Extract key metrics from parameters
            for param, pdata in cdata.parameters.items():
                if hasattr(pdata, 'values') and pdata.values:
                    vals = list(pdata.values.values())
                    climate_data[f"{param.lower()}_avg"] = sum(v for v in vals if v is not None) / len([v for v in vals if v is not None]) if vals else 0
                    climate_data[f"{param.lower()}_sum"] = sum(v for v in vals if v is not None)

    if collected.soil_moisture and collected.soil_moisture.data:
        # Extract soil info if available
        pass

    if collected.gaez and collected.gaez.data:
        gaez_data = collected.gaez.data
        soil_data = collected.gaez.data.get("soil_constraints", {})
        soil_data.update(collected.gaez.data.get("agro_climatic", {}))

    # 4. Crop suitability analysis
    ag_service = get_agricultural_analysis_service()
    crop_suitability = ag_service.recommend_crops(
        climate_data=climate_data,
        soil_data=soil_data,
        gaez_data=gaez_data,
        top_n=8
    )

    # 5. Risk assessment for top 3 crops
    risk_assessments = []
    for crop_score in crop_suitability[:3]:
        risks = ag_service.assess_risks(
            crop=crop_score.crop,
            climate_data=climate_data,
            soil_data=soil_data,
            ndvi_data=None
        )
        for risk in risks:
            risk_assessments.append({
                "crop": crop_score.crop,
                "risk_type": risk.risk_type,
                "level": risk.level.value,
                "probability": risk.probability,
                "impact": risk.impact,
                "description": risk.description,
                "mitigation": risk.mitigation,
                "indicators": risk.indicators
            })

    # 6. Yield gap analysis for top crops
    yield_gaps = []
    for crop_score in crop_suitability[:5]:
        yg = ag_service.estimate_yield_gap(
            crop=crop_score.crop,
            climate_data=climate_data,
            soil_data=soil_data,
            management_level="medium"
        )
        if "error" not in yg:
            yield_gaps.append(yg)

    # 7. Generate recommendations
    recommendations = _generate_recommendations(
        crop_suitability, risk_assessments, yield_gaps, validation_results
    )

    return AnalysisResponse(
        farm_id=farm_id,
        farm_name=farm["name"],
        latitude=farm["latitude"],
        longitude=farm["longitude"],
        analysis_date=datetime.utcnow(),
        period={"start": start.isoformat(), "end": end.isoformat()},
        data_collection=collected.to_dict(),
        validation=validation_results,
        crop_suitability=[{
            "crop": s.crop,
            "overall_score": s.overall_score,
            "temperature_score": s.temperature_score,
            "water_score": s.water_score,
            "soil_score": s.soil_score,
            "frost_score": s.frost_score,
            "limiting_factors": s.limiting_factors,
            "potential_yield": s.potential_yield
        } for s in crop_suitability],
        risk_assessment=risk_assessments,
        yield_gaps=yield_gaps,
        recommendations=recommendations
    )


def _score_to_dict(score) -> Dict[str, Any]:
    """Convert SuitabilityScore dataclass to dict with native Python types"""
    return {
        "crop": score.crop,
        "overall_score": float(score.overall_score),
        "temperature_score": float(score.temperature_score),
        "water_score": float(score.water_score),
        "soil_score": float(score.soil_score),
        "frost_score": float(score.frost_score),
        "limiting_factors": score.limiting_factors,
        "potential_yield": float(score.potential_yield) if score.potential_yield is not None else None
    }


@router.post("/crop-suitability", response_model=List[Dict[str, Any]])
async def analyze_crop_suitability(request: CropSuitabilityRequest):
    """Analyze crop suitability for a location."""
    ag_service = get_agricultural_analysis_service()

    if request.crops:
        results = []
        for crop in request.crops:
            score = ag_service.assess_crop_suitability(
                crop, request.climate_data or {}, request.soil_data or {}, request.gaez_data
            )
            results.append(_score_to_dict(score))
        return results
    else:
        scores = ag_service.recommend_crops(
            climate_data=request.climate_data or {},
            soil_data=request.soil_data or {},
            gaez_data=request.gaez_data,
            top_n=10
        )
        return [_score_to_dict(s) for s in scores]


@router.post("/water-balance", response_model=Dict[str, Any])
async def calculate_water_balance(request: WaterBalanceRequest):
    """Calculate water balance for a crop."""
    ag_service = get_agricultural_analysis_service()

    # We need daily climate data - for now return structure
    # In production, this would fetch from climate connectors
    daily_climate = []  # Would be fetched from NASA POWER

    # For demo, create mock daily data
    from datetime import timedelta
    current = request.start_date
    while current <= request.end_date:
        daily_climate.append({
            "date": current.isoformat(),
            "precipitation": 2.5,  # mm/day average
            "tmin": 15,
            "tmax": 28,
            "rh": 65,
            "wind": 3,
            "solar_rad": 22
        })
        current += timedelta(days=1)

    soil_data = request.soil_data or {
        "field_capacity": 0.3,
        "wilting_point": 0.15,
        "rooting_depth": 100
    }

    result = ag_service.calculate_water_balance(
        crop=request.crop,
        daily_climate=daily_climate,
        soil_data=soil_data,
        irrigation_schedule=request.irrigation_schedule
    )

    return {
        "period_start": result.period_start.isoformat(),
        "period_end": result.period_end.isoformat(),
        "precipitation_mm": result.precipitation,
        "et0_mm": result.et0,
        "etc_mm": result.etc,
        "irrigation_requirement_mm": result.irrigation_req,
        "runoff_mm": result.runoff,
        "drainage_mm": result.drainage,
        "soil_moisture_change_mm": result.soil_moisture_change,
        "water_stress_days": result.water_stress_days,
        "deficit_days": result.deficit_days,
        "water_use_efficiency": round(result.etc / max(result.precipitation, 1), 2)
    }


@router.post("/rotation", response_model=Dict[str, Any])
async def analyze_rotation(request: RotationRequest):
    """Analyze crop rotation options."""
    ag_service = get_agricultural_analysis_service()

    result = ag_service.analyze_rotation(
        current_crop=request.current_crop,
        proposed_crops=request.proposed_crops,
        soil_data=request.soil_data or {},
        climate_data=request.climate_data or {}
    )

    return {
        "current_crop": result.current_crop,
        "proposed_crops": result.proposed_crops,
        "benefits": result.benefits,
        "risks": result.risks,
        "sustainability_score": result.sustainability_score,
        "nitrogen_balance_kg_ha": result.nitrogen_balance,
        "disease_break": result.disease_break,
        "weed_management": result.weed_management
    }


@router.post("/risk-assessment", response_model=List[Dict[str, Any]])
async def assess_risks(request: RiskAssessmentRequest):
    """Assess agricultural risks for a crop."""
    ag_service = get_agricultural_analysis_service()

    risks = ag_service.assess_risks(
        crop=request.crop,
        climate_data=request.climate_data or {},
        soil_data=request.soil_data or {},
        ndvi_data=request.ndvi_data
    )

    return [{
        "risk_type": r.risk_type,
        "level": r.level.value,
        "probability": r.probability,
        "impact": r.impact,
        "description": r.description,
        "mitigation": r.mitigation,
        "indicators": r.indicators
    } for r in risks]


@router.post("/yield-gap", response_model=Dict[str, Any])
async def estimate_yield_gap(request: YieldGapRequest):
    """Estimate yield gap for a crop."""
    ag_service = get_agricultural_analysis_service()

    result = ag_service.estimate_yield_gap(
        crop=request.crop,
        climate_data=request.climate_data or {},
        soil_data=request.soil_data or {},
        management_level=request.management_level
    )

    return result


@router.post("/ndvi-time-series", response_model=Dict[str, Any])
async def create_ndvi_time_series(
    farm_id: str,
    observations: List[Dict[str, Any]]
):
    """Create NDVI time series from satellite observations."""
    farm = farms_db.get(farm_id)
    if not farm:
        raise HTTPException(status_code=404, detail="Farm not found")

    geo_service = get_geospatial_analysis_service()
    ts = geo_service.create_ndvi_time_series(
        latitude=farm["latitude"],
        longitude=farm["longitude"],
        observations=observations
    )

    return {
        "latitude": ts.latitude,
        "longitude": ts.longitude,
        "points": [
            {"date": p.date, "value": p.value, "quality": p.quality, "metadata": p.metadata}
            for p in ts.points
        ],
        "statistics": ts.statistics
    }


@router.post("/ndvi/phenology", response_model=Dict[str, Any])
async def analyze_phenology(
    farm_id: str,
    observations: List[Dict[str, Any]]
):
    """Analyze phenology from NDVI time series."""
    farm = farms_db.get(farm_id)
    if not farm:
        raise HTTPException(status_code=404, detail="Farm not found")

    geo_service = get_geospatial_analysis_service()
    ts = geo_service.create_ndvi_time_series(
        latitude=farm["latitude"],
        longitude=farm["longitude"],
        observations=observations
    )

    phenology = geo_service.calculate_phenology(ts.points)
    anomalies = geo_service.detect_anomalies(ts.points)

    return {
        "phenology": phenology,
        "anomalies": anomalies,
        "statistics": ts.statistics
    }


@router.get("/vegetation-indices", response_model=Dict[str, Any])
async def calculate_indices(
    nir: float = Query(...),
    red: float = Query(...),
    blue: Optional[float] = Query(None),
    green: Optional[float] = Query(None),
    swir: Optional[float] = Query(None)
):
    """Calculate all vegetation indices from band values."""
    geo_service = get_geospatial_analysis_service()

    bands = {"nir": nir, "red": red}
    if blue: bands["blue"] = blue
    if green: bands["green"] = green
    if swir: bands["swir"] = swir

    indices = geo_service.calculate_all_indices(bands)

    # Add interpretations
    result: Dict[str, Any] = {}
    for idx, value in indices.items():
        result[idx] = round(float(value), 4)
        if idx == "ndvi":
            interp = geo_service.interpret_ndvi(value)
            result[f"{idx}_class"] = interp["class"]
            result[f"{idx}_description"] = interp["description"]

    return result


def _generate_recommendations(
    crop_suitability: List,
    risk_assessments: List,
    yield_gaps: List,
    validation: Dict
) -> List[str]:
    """Generate actionable recommendations from analysis."""
    recommendations = []

    # Top crop recommendation
    if crop_suitability:
        top = crop_suitability[0]
        recommendations.append(
            f"Top recommended crop: {top.crop} (suitability: {top.overall_score}/100)"
        )

        if top.limiting_factors:
            recommendations.append(
                f"Main limiting factors for {top.crop}: {', '.join(top.limiting_factors)}"
            )

    # Risk-based recommendations
    high_risks = [r for r in risk_assessments if r["level"] in ["high", "very_high"]]
    if high_risks:
        risk_types = set(r["risk_type"] for r in high_risks)
        recommendations.append(
            f"High priority risks to address: {', '.join(risk_types)}"
        )

        for risk in high_risks[:3]:
            if risk["mitigation"]:
                recommendations.append(
                    f"For {risk['risk_type']}: {risk['mitigation'][0]}"
                )

    # Yield gap recommendations
    for yg in yield_gaps[:3]:
        if yg.get("yield_gap_attainable", 0) > 1.0:
            recommendations.append(
                f"{yg['crop']}: Yield gap of {yg['yield_gap_attainable']:.1f} t/ha. "
                f"Limiting factors: {', '.join(yg.get('limiting_factors', []))}"
            )

    # Data quality recommendations
    poor_sources = [k for k, v in validation.items() if isinstance(v, dict) and v.get("quality") in ["poor", "unusable"]]
    if poor_sources:
        recommendations.append(
            f"Data quality issues with: {', '.join(poor_sources)}. Consider alternative sources."
        )

    return recommendations