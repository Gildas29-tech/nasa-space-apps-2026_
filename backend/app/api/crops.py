from fastapi import APIRouter, HTTPException, Query
from pydantic import BaseModel, Field
from typing import Optional, List, Dict
from datetime import date

router = APIRouter()

# Crop database with agronomic requirements
CROP_DATABASE = {
    "wheat": {
        "name": "Blé tendre",
        "icon": "🌾",
        "season": "winter",
        "water_need": "medium",
        "temp_optimal_min": 10,
        "temp_optimal_max": 25,
        "frost_tolerance": "high",
        "growth_days": 240,
        "soil_ph_min": 6.0,
        "soil_ph_max": 7.5,
        "soil_texture_preference": ["clay", "loam", "silt"],
        "nitrogen_need": "high",
        "crop_family": "Poaceae",
    },
    "barley": {
        "name": "Orge",
        "icon": "🌾",
        "season": "winter_spring",
        "water_need": "low_medium",
        "temp_optimal_min": 8,
        "temp_optimal_max": 22,
        "frost_tolerance": "medium",
        "growth_days": 180,
        "soil_ph_min": 6.0,
        "soil_ph_max": 7.5,
        "soil_texture_preference": ["loam", "silt"],
        "nitrogen_need": "medium",
        "crop_family": "Poaceae",
    },
    "maize": {
        "name": "Maïs",
        "icon": "🌽",
        "season": "summer",
        "water_need": "high",
        "temp_optimal_min": 18,
        "temp_optimal_max": 32,
        "frost_tolerance": "none",
        "growth_days": 150,
        "soil_ph_min": 5.8,
        "soil_ph_max": 7.2,
        "soil_texture_preference": ["loam", "clay_loam"],
        "nitrogen_need": "very_high",
        "crop_family": "Poaceae",
    },
    "sunflower": {
        "name": "Tournesol",
        "icon": "🌻",
        "season": "summer",
        "water_need": "medium",
        "temp_optimal_min": 18,
        "temp_optimal_max": 28,
        "frost_tolerance": "low",
        "growth_days": 120,
        "soil_ph_min": 6.0,
        "soil_ph_max": 7.5,
        "soil_texture_preference": ["loam", "clay_loam"],
        "nitrogen_need": "medium",
        "crop_family": "Asteraceae",
    },
    "rapeseed": {
        "name": "Colza",
        "icon": "🌱",
        "season": "winter",
        "water_need": "medium_high",
        "temp_optimal_min": 8,
        "temp_optimal_max": 22,
        "frost_tolerance": "high",
        "growth_days": 300,
        "soil_ph_min": 6.0,
        "soil_ph_max": 7.5,
        "soil_texture_preference": ["clay", "clay_loam"],
        "nitrogen_need": "high",
        "crop_family": "Brassicaceae",
    },
    "soybean": {
        "name": "Soja",
        "icon": "🫘",
        "season": "summer",
        "water_need": "medium_high",
        "temp_optimal_min": 18,
        "temp_optimal_max": 30,
        "frost_tolerance": "none",
        "growth_days": 130,
        "soil_ph_min": 6.0,
        "soil_ph_max": 7.0,
        "soil_texture_preference": ["loam", "clay_loam"],
        "nitrogen_need": "low",  # Fixes nitrogen
        "crop_family": "Fabaceae",
    },
    "sorghum": {
        "name": "Sorgho",
        "icon": "🌾",
        "season": "summer",
        "water_need": "low",
        "temp_optimal_min": 22,
        "temp_optimal_max": 35,
        "frost_tolerance": "none",
        "growth_days": 120,
        "soil_ph_min": 5.5,
        "soil_ph_max": 7.5,
        "soil_texture_preference": ["loam", "sandy_loam", "clay_loam"],
        "nitrogen_need": "medium",
        "crop_family": "Poaceae",
    },
    "pea": {
        "name": "Pois protéagineux",
        "icon": "🫛",
        "season": "winter_spring",
        "water_need": "low_medium",
        "temp_optimal_min": 8,
        "temp_optimal_max": 22,
        "frost_tolerance": "medium",
        "growth_days": 180,
        "soil_ph_min": 6.0,
        "soil_ph_max": 7.5,
        "soil_texture_preference": ["loam", "clay_loam"],
        "nitrogen_need": "low",  # Fixes nitrogen
        "crop_family": "Fabaceae",
    },
}


class FarmContext(BaseModel):
    latitude: float
    longitude: float
    avg_temperature: float
    annual_precipitation: float
    soil_ph: Optional[float] = None
    soil_texture: Optional[str] = None
    water_capacity: Optional[str] = None
    frost_days: int = 0
    growing_season_start: int = 4
    growing_season_end: int = 10


class CropSuitability(BaseModel):
    crop_id: str
    name: str
    icon: str
    overall_score: int
    suitability: str
    details: Dict[str, int]
    season: str
    water_need: str
    growth_days: int
    frost_tolerance: str
    temp_optimal: str
    advantages: List[str]
    limitations: List[str]
    recommendations: List[str]


class CropComparisonRequest(BaseModel):
    farm_context: FarmContext
    crop_ids: List[str]


class RotationYear(BaseModel):
    year: int
    crop_id: Optional[str] = None


class RotationRequest(BaseModel):
    farm_context: FarmContext
    years: List[RotationYear]


def calculate_crop_suitability(crop: dict, context: FarmContext) -> CropSuitability:
    """Calculate suitability score for a crop given farm context"""
    scores = {}

    # Temperature score (0-100)
    temp_score = 100
    if context.avg_temperature < crop["temp_optimal_min"]:
        temp_score = max(0, 100 - (crop["temp_optimal_min"] - context.avg_temperature) * 10)
    elif context.avg_temperature > crop["temp_optimal_max"]:
        temp_score = max(0, 100 - (context.avg_temperature - crop["temp_optimal_max"]) * 10)
    scores["temp"] = round(temp_score)

    # Water score (0-100)
    water_map = {"low": 300, "low_medium": 500, "medium": 700, "medium_high": 900, "high": 1100, "very_high": 1300}
    crop_water_need = water_map.get(crop["water_need"], 700)
    water_score = max(0, 100 - abs(context.annual_precipitation - crop_water_need) / 10)
    scores["water"] = round(water_score)

    # Soil pH score (0-100)
    if context.soil_ph and crop["soil_ph_min"] and crop["soil_ph_max"]:
        if context.soil_ph < crop["soil_ph_min"]:
            ph_score = max(0, 100 - (crop["soil_ph_min"] - context.soil_ph) * 50)
        elif context.soil_ph > crop["soil_ph_max"]:
            ph_score = max(0, 100 - (context.soil_ph - crop["soil_ph_max"]) * 50)
        else:
            ph_score = 100
    else:
        ph_score = 70  # Unknown soil pH
    scores["soil"] = round(ph_score)

    # Frost score (0-100)
    frost_map = {"none": 0, "low": 30, "medium": 60, "high": 90}
    crop_frost = frost_map.get(crop["frost_tolerance"], 50)
    if context.frost_days > 60:
        frost_score = max(0, crop_frost - (context.frost_days - 60) * 2)
    else:
        frost_score = crop_frost
    scores["frost"] = round(frost_score)

    # Overall score (weighted average)
    weights = {"temp": 0.3, "water": 0.25, "soil": 0.25, "frost": 0.2}
    overall = sum(scores[k] * weights[k] for k in weights)
    overall_score = round(overall)

    # Suitability label
    if overall_score >= 85:
        suitability = "Très adapté"
    elif overall_score >= 70:
        suitability = "Bien adapté"
    elif overall_score >= 55:
        suitability = "Adapté avec conditions"
    else:
        suitability = "Peu adapté"

    # Advantages & limitations
    advantages = []
    limitations = []

    if scores["temp"] >= 80:
        advantages.append("Température optimale pour cette culture")
    elif scores["temp"] < 50:
        limitations.append("Température hors plage optimale")

    if scores["water"] >= 80:
        advantages.append("Précipitations bien adaptées aux besoins en eau")
    elif scores["water"] < 50:
        limitations.append("Déficit ou excès hydrique probable - irrigation/drainage nécessaire")

    if scores["soil"] >= 80:
        advantages.append("pH du sol optimal")
    elif scores["soil"] < 50:
        limitations.append("pH du sol non optimal - amendement nécessaire")

    if scores["frost"] >= 70:
        advantages.append("Bonne tolérance au gel pour la zone")
    elif scores["frost"] < 40:
        limitations.append("Sensible au gel - attention aux semis précoces")

    if crop["nitrogen_need"] == "low":
        advantages.append("Faible besoin en azote (fixation atmosphérique)")

    # Recommendations
    recommendations = []
    if scores["water"] < 60:
        recommendations.append("Prévoir un système d'irrigation de secours")
    if scores["soil"] < 60:
        recommendations.append("Analyse de sol recommandée pour ajustement pH")
    if scores["frost"] < 50:
        recommendations.append("Choisir des variétés à cycle court ou tolérantes au gel")
    if crop["crop_family"] == "Poaceae" and context.soil_texture == "clay":
        recommendations.append("Sol argileux - surveiller l'asphyxie racinaire")

    return CropSuitability(
        crop_id=crop["name"].lower().replace(" ", "_"),
        name=crop["name"],
        icon=crop["icon"],
        overall_score=overall_score,
        suitability=suitability,
        details=scores,
        season=crop["season"],
        water_need=crop["water_need"],
        growth_days=crop["growth_days"],
        frost_tolerance=crop["frost_tolerance"],
        temp_optimal=f"{crop['temp_optimal_min']}-{crop['temp_optimal_max']}°C",
        advantages=advantages,
        limitations=limitations,
        recommendations=recommendations,
    )


@router.get("/catalog", response_model=List[dict])
async def get_crop_catalog():
    """Get list of all available crops with basic info"""
    return [
        {
            "id": key,
            "name": val["name"],
            "icon": val["icon"],
            "season": val["season"],
            "water_need": val["water_need"],
            "frost_tolerance": val["frost_tolerance"],
            "growth_days": val["growth_days"],
            "crop_family": val["crop_family"],
        }
        for key, val in CROP_DATABASE.items()
    ]


@router.get("/{crop_id}", response_model=dict)
async def get_crop_details(crop_id: str):
    """Get detailed information for a specific crop"""
    crop = CROP_DATABASE.get(crop_id)
    if not crop:
        raise HTTPException(status_code=404, detail="Culture non trouvée")
    return {"id": crop_id, **crop}


@router.post("/compare", response_model=List[CropSuitability])
async def compare_crops(request: CropComparisonRequest):
    """Compare multiple crops for a given farm context"""
    results = []
    for crop_id in request.crop_ids:
        crop = CROP_DATABASE.get(crop_id)
        if not crop:
            continue
        suitability = calculate_crop_suitability(crop, request.farm_context)
        results.append(suitability)

    # Sort by overall score descending
    results.sort(key=lambda x: x.overall_score, reverse=True)
    return results


@router.post("/rotation/analyze", response_model=dict)
async def analyze_rotation(request: RotationRequest):
    """Analyze a crop rotation plan"""
    rotation = []
    families = []
    issues = []
    benefits = []

    for yr in request.years:
        if yr.crop_id and yr.crop_id in CROP_DATABASE:
            crop = CROP_DATABASE[yr.crop_id]
            rotation.append({"year": yr.year, "crop": crop["name"], "family": crop["crop_family"]})
            families.append(crop["crop_family"])
        else:
            rotation.append({"year": yr.year, "crop": "Jachère / Culture intermédiaire", "family": "None"})

    # Analyze rotation
    family_counts = {}
    for f in families:
        if f != "None":
            family_counts[f] = family_counts.get(f, 0) + 1

    # Check for consecutive same family
    for i in range(len(families) - 1):
        if families[i] == families[i + 1] and families[i] != "None":
            issues.append({
                "type": "consecutive_same_family",
                "severity": "warning",
                "message": f"Deux cultures de la même famille ({families[i]}) consécutives - risque maladies",
                "years": [rotation[i]["year"], rotation[i + 1]["year"]],
            })

    # Check diversity
    if len(set(f for f in families if f != "None")) >= 3:
        benefits.append({
            "type": "high_diversity",
            "message": f"{len(set(f for f in families if f != 'None'))} familles botaniques différentes - excellente diversité",
        })
    elif len(set(f for f in families if f != "None")) >= 2:
        benefits.append({
            "type": "medium_diversity",
            "message": f"{len(set(f for f in families if f != 'None'))} familles botaniques - bonne diversité",
        })
    else:
        issues.append({
            "type": "low_diversity",
            "severity": "warning",
            "message": "Faible diversité culturale - risque accumulation parasites",
        })

    # Check nitrogen fixation
    legume_years = [r for r in rotation if r["family"] == "Fabaceae"]
    if legume_years:
        benefits.append({
            "type": "nitrogen_fixation",
            "message": f"Légumineuses présentes ({len(legume_years)} an(s)) - apport azote naturel",
        })
    else:
        issues.append({
            "type": "no_legume",
            "severity": "info",
            "message": "Aucune légumineuse dans la rotation - dépendance engrais azotés",
        })

    # Winter/Summer alternation
    seasons = []
    for r in rotation:
        if r["crop"] != "Jachère / Culture intermédiaire" and r["crop_id"] in CROP_DATABASE:
            crop = CROP_DATABASE[r["crop_id"]]
            seasons.append(crop["season"])
    winter_count = sum(1 for s in seasons if "winter" in s)
    summer_count = sum(1 for s in seasons if "summer" in s)
    if winter_count > 0 and summer_count > 0:
        benefits.append({
            "type": "seasonal_alternation",
            "message": "Alternance cultures hiver/été - bon pour gestion adventices et sol",
        })

    return {
        "rotation": rotation,
        "analysis": {
            "diversity_score": min(100, len(set(f for f in families if f != "None")) * 25),
            "family_distribution": family_counts,
            "issues": issues,
            "benefits": benefits,
            "recommendations": [
                "Intégrer une légumineuse tous les 2-3 ans" if not legume_years else "Maintenir les légumineuses dans la rotation",
                "Éviter les cultures de même famille consécutives" if any(i["type"] == "consecutive_same_family" for i in issues) else "Bonne alternance des familles",
                "Considérer cultures de couverture entre cultures principales",
            ],
        },
    }


@router.get("/rotation/suggest", response_model=List[dict])
async def suggest_rotations(
    farm_context: FarmContext,
    duration_years: int = Query(5, ge=3, le=10),
    include_legume: bool = True,
):
    """Suggest crop rotation sequences based on farm context"""
    # Get suitable crops
    suitable_crops = []
    for crop_id, crop in CROP_DATABASE.items():
        suitability = calculate_crop_suitability(crop, farm_context)
        if suitability.overall_score >= 60:
            suitable_crops.append((crop_id, crop, suitability.overall_score))

    suitable_crops.sort(key=lambda x: x[2], reverse=True)

    # Generate rotation suggestions
    suggestions = []

    # Suggestion 1: Classic cereal rotation
    cereal_crops = [c for c in suitable_crops if c[1]["crop_family"] == "Poaceae"]
    legume_crops = [c for c in suitable_crops if c[1]["crop_family"] == "Fabaceae"]
    other_crops = [c for c in suitable_crops if c[1]["crop_family"] not in ["Poaceae", "Fabaceae"]]

    if cereal_crops and legume_crops:
        rotation = []
        for i in range(duration_years):
            if i % 3 == 0 and legume_crops:
                rotation.append(legume_crops[0][0])
            elif cereal_crops:
                rotation.append(cereal_crops[i % len(cereal_crops)][0])
            elif other_crops:
                rotation.append(other_crops[0][0])
        suggestions.append({
            "name": "Rotation céréales-légumineuses classique",
            "description": "Alternance céréales d'hiver et légumineuses de printemps",
            "rotation": rotation,
            "suitable": True,
        })

    # Suggestion 2: Diversified rotation
    if len(suitable_crops) >= 3:
        families_used = set()
        rotation = []
        for i in range(duration_years):
            for crop_id, crop, score in suitable_crops:
                if crop["crop_family"] not in families_used or len(families_used) >= 3:
                    rotation.append(crop_id)
                    families_used.add(crop["crop_family"])
                    break
        suggestions.append({
            "name": "Rotation diversifiée multi-espèces",
            "description": "Maximise la diversité des familles botaniques",
            "rotation": rotation,
            "suitable": True,
        })

    # Suggestion 3: Climate adaptation
    if farm_context.avg_temperature > 15:
        summer_crops = [c for c in suitable_crops if c[1]["season"] == "summer"]
        if summer_crops:
            rotation = []
            for i in range(duration_years):
                rotation.append(summer_crops[i % len(summer_crops)][0])
            suggestions.append({
                "name": "Rotation adaptée climat chaud",
                "description": "Cultures d'été tolérantes à la chaleur et au stress hydrique",
                "rotation": rotation,
                "suitable": True,
            })

    return suggestions