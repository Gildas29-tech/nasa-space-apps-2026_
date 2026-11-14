"""
Agricultural Analysis Service
Crop suitability, rotation planning, water balance, and risk assessment.
"""
from datetime import date, datetime
from typing import Optional, Dict, Any, List, Tuple
from dataclasses import dataclass, field
from enum import Enum
import math
import numpy as np


class CropType(str, Enum):
    """Supported crop types"""
    WHEAT = "wheat"
    MAIZE = "maize"
    RICE = "rice"
    SOYBEAN = "soybean"
    SORGHUM = "sorghum"
    SUNFLOWER = "sunflower"
    RAPESEED = "rapeseed"
    BARLEY = "barley"
    COTTON = "cotton"
    SUGARCANE = "sugarcane"
    POTATO = "potato"
    TOMATO = "tomato"


class WaterSupply(str, Enum):
    RAINFED = "rainfed"
    IRRIGATED = "irrigated"


class InputLevel(str, Enum):
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"


class RiskLevel(str, Enum):
    VERY_LOW = "very_low"
    LOW = "low"
    MODERATE = "moderate"
    HIGH = "high"
    VERY_HIGH = "very_high"


@dataclass
class CropRequirements:
    """Crop climatic and soil requirements"""
    name: str
    # Temperature requirements (°C)
    t_base: float = 0          # Base temperature for growth
    t_opt_min: float = 15      # Optimum minimum temperature
    t_opt_max: float = 30      # Optimum maximum temperature
    t_max: float = 40          # Maximum temperature
    # Growing degree days
    gdd_min: float = 1000      # Minimum GDD to maturity
    gdd_opt: float = 2000      # Optimum GDD
    # Water requirements (mm/season)
    water_min: float = 300
    water_opt: float = 600
    water_max: float = 1200
    # Frost tolerance
    frost_tolerance: float = -2  # °C
    # Soil requirements
    ph_min: float = 5.5
    ph_opt_min: float = 6.0
    ph_opt_max: float = 7.5
    ph_max: float = 8.5
    # Soil texture preference (1=sand, 2=loam, 3=clay)
    texture_preference: List[int] = field(default_factory=lambda: [2])
    # Salinity tolerance (dS/m)
    salinity_max: float = 4.0
    # Rooting depth (cm)
    rooting_depth: float = 100
    # Crop calendar (day of year)
    planting_window_start: int = 60   # ~March 1
    planting_window_end: int = 150    # ~May 30
    harvest_window_start: int = 200   # ~July 20
    harvest_window_end: int = 300     # ~Oct 30


@dataclass
class SuitabilityScore:
    """Crop suitability assessment"""
    crop: str
    overall_score: float  # 0-100
    temperature_score: float
    water_score: float
    soil_score: float
    frost_score: float
    limiting_factors: List[str] = field(default_factory=list)
    potential_yield: Optional[float] = None  # t/ha
    yield_gap: Optional[float] = None  # t/ha


@dataclass
class WaterBalanceResult:
    """Water balance calculation result"""
    period_start: date
    period_end: date
    precipitation: float  # mm
    et0: float  # mm reference evapotranspiration
    etc: float  # mm crop evapotranspiration
    irrigation_req: float  # mm
    runoff: float  # mm
    drainage: float  # mm
    soil_moisture_change: float  # mm
    water_stress_days: int
    deficit_days: int


@dataclass
class RotationAnalysis:
    """Crop rotation analysis"""
    current_crop: str
    proposed_crops: List[str]
    benefits: List[str]
    risks: List[str]
    sustainability_score: float
    nitrogen_balance: float  # kg/ha
    disease_break: Dict[str, bool]
    weed_management: Dict[str, bool]


@dataclass
class RiskAssessment:
    """Agricultural risk assessment"""
    risk_type: str
    level: RiskLevel
    probability: float  # 0-1
    impact: str
    description: str
    mitigation: List[str]
    indicators: Dict[str, float]


# Crop requirements database
CROP_REQUIREMENTS = {
    CropType.WHEAT: CropRequirements(
        name="Wheat",
        t_base=0, t_opt_min=12, t_opt_max=25, t_max=35,
        gdd_min=1300, gdd_opt=1800,
        water_min=300, water_opt=500, water_max=800,
        frost_tolerance=-5,
        ph_min=5.5, ph_opt_min=6.0, ph_opt_max=7.5, ph_max=8.5,
        texture_preference=[2, 3],
        salinity_max=6.0,
        rooting_depth=120,
        planting_window_start=270,  # Sep 27 (winter wheat)
        planting_window_end=330,    # Nov 26
        harvest_window_start=180,   # Jun 29
        harvest_window_end=230      # Aug 18
    ),
    CropType.MAIZE: CropRequirements(
        name="Maize",
        t_base=10, t_opt_min=18, t_opt_max=32, t_max=45,
        gdd_min=1800, gdd_opt=2500,
        water_min=400, water_opt=600, water_max=1000,
        frost_tolerance=0,
        ph_min=5.5, ph_opt_min=5.8, ph_opt_max=7.0, ph_max=8.0,
        texture_preference=[2],
        salinity_max=1.7,
        rooting_depth=150,
        planting_window_start=90,   # Mar 31
        planting_window_end=150,    # May 30
        harvest_window_start=240,   # Aug 28
        harvest_window_end=300      # Oct 27
    ),
    CropType.RICE: CropRequirements(
        name="Rice",
        t_base=10, t_opt_min=20, t_opt_max=35, t_max=42,
        gdd_min=2000, gdd_opt=3000,
        water_min=800, water_opt=1200, water_max=2000,
        frost_tolerance=0,
        ph_min=5.0, ph_opt_min=5.5, ph_opt_max=7.0, ph_max=8.0,
        texture_preference=[3],  # Clay preferred
        salinity_max=3.0,
        rooting_depth=50,
        planting_window_start=90,
        planting_window_end=180,
        harvest_window_start=240,
        harvest_window_end=330
    ),
    CropType.SOYBEAN: CropRequirements(
        name="Soybean",
        t_base=10, t_opt_min=20, t_opt_max=30, t_max=40,
        gdd_min=1500, gdd_opt=2200,
        water_min=350, water_opt=550, water_max=900,
        frost_tolerance=-1,
        ph_min=5.5, ph_opt_min=6.0, ph_opt_max=7.0, ph_max=8.0,
        texture_preference=[2],
        salinity_max=5.0,
        rooting_depth=100,
        planting_window_start=120,
        planting_window_end=180,
        harvest_window_start=270,
        harvest_window_end=320
    ),
    CropType.SORGHUM: CropRequirements(
        name="Sorghum",
        t_base=12, t_opt_min=25, t_opt_max=35, t_max=45,
        gdd_min=1800, gdd_opt=2500,
        water_min=300, water_opt=500, water_max=800,
        frost_tolerance=0,
        ph_min=5.0, ph_opt_min=5.5, ph_opt_max=7.5, ph_max=8.5,
        texture_preference=[1, 2],
        salinity_max=4.0,
        rooting_depth=180,
        planting_window_start=120,
        planting_window_end=180,
        harvest_window_start=270,
        harvest_window_end=330
    ),
    CropType.SUNFLOWER: CropRequirements(
        name="Sunflower",
        t_base=6, t_opt_min=18, t_opt_max=28, t_max=40,
        gdd_min=1600, gdd_opt=2200,
        water_min=300, water_opt=500, water_max=800,
        frost_tolerance=-2,
        ph_min=5.5, ph_opt_min=6.0, ph_opt_max=7.5, ph_max=8.5,
        texture_preference=[2],
        salinity_max=4.5,
        rooting_depth=200,
        planting_window_start=90,
        planting_window_end=150,
        harvest_window_start=240,
        harvest_window_end=300
    ),
    CropType.RAPESEED: CropRequirements(
        name="Rapeseed",
        t_base=0, t_opt_min=10, t_opt_max=25, t_max=35,
        gdd_min=1400, gdd_opt=2000,
        water_min=350, water_opt=550, water_max=900,
        frost_tolerance=-8,
        ph_min=5.5, ph_opt_min=6.0, ph_opt_max=7.5, ph_max=8.5,
        texture_preference=[2, 3],
        salinity_max=3.5,
        rooting_depth=150,
        planting_window_start=240,  # Aug 28 (winter)
        planting_window_end=300,    # Oct 27
        harvest_window_start=150,   # May 30
        harvest_window_end=200      # Jul 19
    ),
    CropType.BARLEY: CropRequirements(
        name="Barley",
        t_base=0, t_opt_min=12, t_opt_max=25, t_max=35,
        gdd_min=1200, gdd_opt=1700,
        water_min=250, water_opt=450, water_max=750,
        frost_tolerance=-8,
        ph_min=5.5, ph_opt_min=6.0, ph_opt_max=7.5, ph_max=8.5,
        texture_preference=[2, 3],
        salinity_max=8.0,
        rooting_depth=120,
        planting_window_start=270,
        planting_window_end=330,
        harvest_window_start=170,
        harvest_window_end=220
    ),
}


# Crop rotation compatibility matrix
ROTATION_COMPATIBILITY = {
    (CropType.WHEAT, CropType.MAIZE): {"score": 0.8, "notes": "Good break crop"},
    (CropType.WHEAT, CropType.SOYBEAN): {"score": 0.9, "notes": "Excellent - N fixation"},
    (CropType.WHEAT, CropType.SUNFLOWER): {"score": 0.7, "notes": "Good break"},
    (CropType.WHEAT, CropType.RAPESEED): {"score": 0.5, "notes": "Similar disease profile"},
    (CropType.MAIZE, CropType.WHEAT): {"score": 0.8, "notes": "Good rotation"},
    (CropType.MAIZE, CropType.SOYBEAN): {"score": 0.9, "notes": "Classic rotation"},
    (CropType.MAIZE, CropType.RAPESEED): {"score": 0.6, "notes": "Moderate"},
    (CropType.SOYBEAN, CropType.WHEAT): {"score": 0.9, "notes": "Excellent - N benefit"},
    (CropType.SOYBEAN, CropType.MAIZE): {"score": 0.9, "notes": "Classic rotation"},
    (CropType.SOYBEAN, CropType.RAPESEED): {"score": 0.6, "notes": "Moderate"},
    (CropType.RICE, CropType.WHEAT): {"score": 0.7, "notes": "Water management change"},
    (CropType.SORGHUM, CropType.WHEAT): {"score": 0.8, "notes": "Good rotation"},
    (CropType.SUNFLOWER, CropType.WHEAT): {"score": 0.7, "notes": "Good break"},
    (CropType.RAPESEED, CropType.WHEAT): {"score": 0.5, "notes": "Disease risk"},
    (CropType.BARLEY, CropType.MAIZE): {"score": 0.8, "notes": "Good rotation"},
    (CropType.BARLEY, CropType.SOYBEAN): {"score": 0.9, "notes": "Excellent"},
}


class AgriculturalAnalysisService:
    """
    Service for agricultural analysis calculations.

    Includes:
    - Crop suitability assessment
    - Crop rotation planning
    - Water balance calculations
    - Risk assessment (drought, frost, heat, disease)
    - Yield gap analysis
    """

    def __init__(self):
        pass

    def get_crop_requirements(self, crop: str) -> Optional[CropRequirements]:
        """Get crop requirements by name"""
        try:
            return CROP_REQUIREMENTS[CropType(crop.lower())]
        except (ValueError, KeyError):
            return None

    def assess_crop_suitability(
        self,
        crop: str,
        climate_data: Dict[str, Any],
        soil_data: Dict[str, Any],
        gaez_data: Optional[Dict[str, Any]] = None
    ) -> SuitabilityScore:
        """
        Assess crop suitability for a location.

        Args:
            crop: Crop name
            climate_data: Dict with temperature, precipitation, frost_days, etc.
            soil_data: Dict with ph, texture, salinity, depth, etc.
            gaez_data: Optional GAEZ suitability data

        Returns:
            SuitabilityScore with detailed breakdown
        """
        req = self.get_crop_requirements(crop)
        if not req:
            return SuitabilityScore(
                crop=crop,
                overall_score=0,
                temperature_score=0,
                water_score=0,
                soil_score=0,
                frost_score=0,
                limiting_factors=["Unknown crop"]
            )

        # Temperature score
        temp_score = self._score_temperature(req, climate_data)

        # Water score
        water_score = self._score_water(req, climate_data)

        # Soil score
        soil_score = self._score_soil(req, soil_data)

        # Frost score
        frost_score = self._score_frost(req, climate_data)

        # Overall score (weighted average)
        weights = {"temp": 0.3, "water": 0.3, "soil": 0.25, "frost": 0.15}
        overall = (
            temp_score * weights["temp"] +
            water_score * weights["water"] +
            soil_score * weights["soil"] +
            frost_score * weights["frost"]
        )

        # Identify limiting factors
        limiting = []
        if temp_score < 60:
            limiting.append("temperature")
        if water_score < 60:
            limiting.append("water")
        if soil_score < 60:
            limiting.append("soil")
        if frost_score < 60:
            limiting.append("frost")

        # Potential yield from GAEZ if available
        potential_yield = None
        if gaez_data and "crops" in gaez_data:
            for c in gaez_data["crops"]:
                if c["crop"].lower() == crop.lower():
                    potential_yield = c.get("potential_yield")
                    break

        return SuitabilityScore(
            crop=req.name,
            overall_score=round(overall, 1),
            temperature_score=round(temp_score, 1),
            water_score=round(water_score, 1),
            soil_score=round(soil_score, 1),
            frost_score=round(frost_score, 1),
            limiting_factors=limiting,
            potential_yield=potential_yield
        )

    def _score_temperature(self, req: CropRequirements, climate: Dict) -> float:
        """Score temperature suitability (0-100)"""
        # Get average growing season temperature
        t_avg = climate.get("t_avg_growing", climate.get("t2m_avg", 20))
        t_max = climate.get("t_max_growing", climate.get("t2m_max_avg", 30))
        t_min = climate.get("t_min_growing", climate.get("t2m_min_avg", 10))

        # Check if within optimal range
        if req.t_opt_min <= t_avg <= req.t_opt_max:
            base_score = 100
        elif req.t_base <= t_avg <= req.t_max:
            # Linear decline outside optimum
            if t_avg < req.t_opt_min:
                base_score = 100 * (t_avg - req.t_base) / (req.t_opt_min - req.t_base)
            else:
                base_score = 100 * (req.t_max - t_avg) / (req.t_max - req.t_opt_max)
        else:
            base_score = 0

        # Penalize extreme max temps
        if t_max > req.t_max:
            base_score *= 0.5

        # GDD check
        gdd = climate.get("gdd", 0)
        if gdd > 0:
            if gdd >= req.gdd_opt:
                gdd_factor = 1.0
            elif gdd >= req.gdd_min:
                gdd_factor = gdd / req.gdd_opt
            else:
                gdd_factor = 0.3
            base_score *= gdd_factor

        return max(0, min(100, base_score))

    def _score_water(self, req: CropRequirements, climate: Dict) -> float:
        """Score water suitability (0-100)"""
        # Growing season precipitation
        precip = climate.get("precip_growing", climate.get("prectotcorr_sum", 500))

        # Adjust for ET0 if available
        et0 = climate.get("et0_growing", 800)
        water_availability = precip  # Simplified - could use P - ET0

        if req.water_min <= water_availability <= req.water_opt:
            return 100
        elif water_availability < req.water_min:
            return max(0, 100 * water_availability / req.water_min)
        elif water_availability <= req.water_max:
            return 100 * (req.water_max - water_availability) / (req.water_max - req.water_opt)
        else:
            return 50  # Excess water - moderate score

    def _score_soil(self, req: CropRequirements, soil: Dict) -> float:
        """Score soil suitability (0-100)"""
        scores = []

        # pH
        ph = soil.get("ph", 7.0)
        if req.ph_opt_min <= ph <= req.ph_opt_max:
            scores.append(100)
        elif req.ph_min <= ph <= req.ph_max:
            if ph < req.ph_opt_min:
                scores.append(100 * (ph - req.ph_min) / (req.ph_opt_min - req.ph_min))
            else:
                scores.append(100 * (req.ph_max - ph) / (req.ph_max - req.ph_opt_max))
        else:
            scores.append(0)

        # Texture
        texture = soil.get("texture", 2)  # 1=sand, 2=loam, 3=clay
        if texture in req.texture_preference:
            scores.append(100)
        else:
            scores.append(50)

        # Salinity
        salinity = soil.get("salinity", 0)
        if salinity <= req.salinity_max * 0.5:
            scores.append(100)
        elif salinity <= req.salinity_max:
            scores.append(100 * (req.salinity_max - salinity) / (req.salinity_max * 0.5))
        else:
            scores.append(0)

        # Depth
        depth = soil.get("depth", 100)
        if depth >= req.rooting_depth:
            scores.append(100)
        else:
            scores.append(100 * depth / req.rooting_depth)

        return np.mean(scores) if scores else 50

    def _score_frost(self, req: CropRequirements, climate: Dict) -> float:
        """Score frost risk (0-100, higher = less risk)"""
        frost_days = climate.get("frost_days", climate.get("frost_free_days", 300))
        min_temp = climate.get("t_min_annual", climate.get("t2m_min_annual", -5))

        # Frost free period check
        if frost_days >= 365 - (req.harvest_window_end - req.planting_window_start):
            ff_score = 100
        elif frost_days >= 180:
            ff_score = 80
        else:
            ff_score = 50

        # Absolute minimum temperature
        if min_temp >= req.frost_tolerance:
            temp_score = 100
        elif min_temp >= req.frost_tolerance - 5:
            temp_score = 60
        else:
            temp_score = 20

        return (ff_score + temp_score) / 2

    def calculate_water_balance(
        self,
        crop: str,
        daily_climate: List[Dict[str, Any]],
        soil_data: Dict[str, Any],
        irrigation_schedule: Optional[List[Dict]] = None
    ) -> WaterBalanceResult:
        """
        Calculate daily water balance for a crop.

        Args:
            crop: Crop name
            daily_climate: List of daily data with precip, tmin, tmax, rh, wind, solar_rad
            soil_data: Soil properties (field_capacity, wilting_point, depth)
            irrigation_schedule: Optional list of irrigation events {date, amount_mm}

        Returns:
            WaterBalanceResult with seasonal totals
        """
        req = self.get_crop_requirements(crop)
        if not req:
            raise ValueError(f"Unknown crop: {crop}")

        # Soil water holding capacity
        fc = soil_data.get("field_capacity", 0.3)  # m3/m3
        wp = soil_data.get("wilting_point", 0.15)  # m3/m3
        depth = soil_data.get("rooting_depth", req.rooting_depth) / 100  # m
        awc = (fc - wp) * depth * 1000  # mm available water capacity

        # Initialize
        soil_moisture = awc * 0.8  # Start at 80% capacity
        irrigation_req = 0
        total_precip = 0
        total_et0 = 0
        total_etc = 0
        total_runoff = 0
        total_drainage = 0
        water_stress_days = 0
        deficit_days = 0

        irrigation_dict = {}
        if irrigation_schedule:
            for irr in irrigation_schedule:
                irrigation_dict[irr["date"]] = irr["amount_mm"]

        for day in daily_climate:
            date_str = day.get("date")
            precip = day.get("precipitation", 0)
            tmin = day.get("tmin", 10)
            tmax = day.get("tmax", 25)
            rh = day.get("rh", 60)
            wind = day.get("wind", 2)
            solar = day.get("solar_rad", 20)

            # Calculate ET0 (Hargreaves-Samani simplified)
            tmean = (tmin + tmax) / 2
            td = tmax - tmin
            ra = solar * 0.408  # Convert MJ/m2 to mm
            et0 = 0.0023 * (tmean + 17.8) * math.sqrt(td) * ra

            # Crop coefficient (simplified - could use growth stage)
            kc = self._get_crop_coefficient(crop, date_str)
            etc = et0 * kc

            # Irrigation
            irrigation = irrigation_dict.get(date_str, 0)

            # Water balance
            water_input = precip + irrigation
            total_precip += precip
            total_et0 += et0
            total_etc += etc
            irrigation_req += irrigation

            # Runoff (simplified - 10% of precip if > 20mm)
            if precip > 20:
                runoff = precip * 0.1
            else:
                runoff = 0
            total_runoff += runoff

            # Effective precipitation
            peff = precip - runoff

            # Soil moisture update
            soil_moisture += peff + irrigation - etc

            # Drainage (excess above field capacity)
            if soil_moisture > awc:
                drainage = soil_moisture - awc
                soil_moisture = awc
                total_drainage += drainage

            # Stress check
            if soil_moisture < awc * 0.5:  # Below 50% AW
                water_stress_days += 1
            if soil_moisture < awc * 0.3:  # Below 30% AW - severe
                deficit_days += 1

            # Prevent negative
            soil_moisture = max(0, soil_moisture)

        return WaterBalanceResult(
            period_start=date.fromisoformat(daily_climate[0]["date"]) if daily_climate else date.today(),
            period_end=date.fromisoformat(daily_climate[-1]["date"]) if daily_climate else date.today(),
            precipitation=round(total_precip, 1),
            et0=round(total_et0, 1),
            etc=round(total_etc, 1),
            irrigation_req=round(irrigation_req, 1),
            runoff=round(total_runoff, 1),
            drainage=round(total_drainage, 1),
            soil_moisture_change=round(soil_moisture - awc * 0.8, 1),
            water_stress_days=water_stress_days,
            deficit_days=deficit_days
        )

    def _get_crop_coefficient(self, crop: str, date_str: str) -> float:
        """Get crop coefficient (Kc) for date"""
        # Simplified - would use actual growth stages
        req = self.get_crop_requirements(crop)
        if not req:
            return 1.0

        try:
            d = date.fromisoformat(date_str)
            doy = d.timetuple().tm_yday

            # Very simplified Kc curve
            season_start = req.planting_window_start
            season_end = req.harvest_window_end

            if doy < season_start or doy > season_end:
                return 0.3  # Off season

            progress = (doy - season_start) / (season_end - season_start)

            if progress < 0.2:
                return 0.4  # Initial
            elif progress < 0.4:
                return 0.8  # Development
            elif progress < 0.7:
                return 1.15  # Mid season
            else:
                return 0.7  # Late season
        except:
            return 1.0

    def analyze_rotation(
        self,
        current_crop: str,
        proposed_crops: List[str],
        soil_data: Dict[str, Any],
        climate_data: Dict[str, Any]
    ) -> RotationAnalysis:
        """
        Analyze crop rotation options.
        """
        current = self.get_crop_requirements(current_crop)
        benefits = []
        risks = []
        disease_break = {}
        weed_management = {}
        total_score = 0
        nitrogen_balance = 0

        for proposed in proposed_crops:
            prop = self.get_crop_requirements(proposed)
            if not prop:
                continue

            # Check rotation compatibility
            key = (CropType(current_crop.lower()), CropType(proposed.lower()))
            reverse_key = (CropType(proposed.lower()), CropType(current_crop.lower()))

            compat = ROTATION_COMPATIBILITY.get(key) or ROTATION_COMPATIBILITY.get(reverse_key)

            if compat:
                total_score += compat["score"]
                benefits.append(f"{prop.name}: {compat['notes']}")

                # Nitrogen balance
                if proposed.lower() == "soybean":
                    nitrogen_balance += 50  # N fixation
                elif current_crop.lower() == "soybean":
                    nitrogen_balance += 30  # Residual N
                else:
                    nitrogen_balance -= 20  # N demand
            else:
                # Default moderate score
                total_score += 0.5

                # Check disease risk
                if current_crop.lower() == proposed.lower():
                    risks.append(f"Continuous {prop.name} - high disease risk")
                    disease_break[proposed] = False
                else:
                    disease_break[proposed] = True

                # Weed management
                if (current_crop.lower() in ["wheat", "barley"] and
                    proposed.lower() in ["maize", "sunflower", "soybean"]):
                    weed_management[proposed] = True
                    benefits.append(f"{prop.name}: Different weed spectrum")
                else:
                    weed_management[proposed] = False

        avg_score = total_score / len(proposed_crops) if proposed_crops else 0

        return RotationAnalysis(
            current_crop=current.name if current else current_crop,
            proposed_crops=proposed_crops,
            benefits=benefits,
            risks=risks,
            sustainability_score=round(avg_score * 100, 1),
            nitrogen_balance=nitrogen_balance,
            disease_break=disease_break,
            weed_management=weed_management
        )

    def assess_risks(
        self,
        crop: str,
        climate_data: Dict[str, Any],
        soil_data: Dict[str, Any],
        ndvi_data: Optional[List[Dict]] = None
    ) -> List[RiskAssessment]:
        """
        Assess agricultural risks for a crop.

        Returns list of RiskAssessment objects.
        """
        risks = []
        req = self.get_crop_requirements(crop)

        if not req:
            return risks

        # 1. Drought risk
        precip = climate_data.get("precip_growing", climate_data.get("prectotcorr_sum", 500))
        et0 = climate_data.get("et0_growing", 800)
        aridity = precip / et0 if et0 > 0 else 1

        if aridity < 0.5:
            level = RiskLevel.VERY_HIGH
        elif aridity < 0.75:
            level = RiskLevel.HIGH
        elif aridity < 1.0:
            level = RiskLevel.MODERATE
        elif aridity < 1.5:
            level = RiskLevel.LOW
        else:
            level = RiskLevel.VERY_LOW

        risks.append(RiskAssessment(
            risk_type="drought",
            level=level,
            probability=max(0, 1 - aridity),
            impact="Yield reduction, crop failure",
            description=f"Aridity index: {aridity:.2f}. Growing season precipitation: {precip:.0f}mm, ET0: {et0:.0f}mm",
            mitigation=[
                "Deficit irrigation scheduling",
                "Drought-tolerant varieties",
                "Conservation tillage",
                "Mulching",
                "Soil organic matter improvement"
            ],
            indicators={"aridity_index": aridity, "precip_mm": precip, "et0_mm": et0}
        ))

        # 2. Heat stress risk
        tmax = climate_data.get("t_max_growing", climate_data.get("t2m_max_avg", 30))
        heat_days = climate_data.get("days_above_35c", 0)

        if tmax > req.t_opt_max + 5 or heat_days > 20:
            level = RiskLevel.HIGH
        elif tmax > req.t_opt_max or heat_days > 10:
            level = RiskLevel.MODERATE
        else:
            level = RiskLevel.LOW

        risks.append(RiskAssessment(
            risk_type="heat_stress",
            level=level,
            probability=min(1.0, heat_days / 30),
            impact="Pollination failure, grain filling reduction",
            description=f"Max temperature: {tmax:.1f}°C (optimum: {req.t_opt_max}°C). Days >35°C: {heat_days}",
            mitigation=[
                "Heat-tolerant varieties",
                "Adjust planting date",
                "Irrigation during flowering",
                "Shade nets (high value crops)"
            ],
            indicators={"max_temp": tmax, "heat_days": heat_days, "optimum_max": req.t_opt_max}
        ))

        # 3. Frost risk
        frost_days = climate_data.get("frost_days", 0)
        tmin = climate_data.get("t_min_annual", climate_data.get("t2m_min_annual", -5))

        if tmin < req.frost_tolerance - 5 or frost_days > 100:
            level = RiskLevel.HIGH
        elif tmin < req.frost_tolerance or frost_days > 50:
            level = RiskLevel.MODERATE
        else:
            level = RiskLevel.LOW

        risks.append(RiskAssessment(
            risk_type="frost",
            level=level,
            probability=min(1.0, frost_days / 100),
            impact="Seedling death, reproductive damage",
            description=f"Min temperature: {tmin:.1f}°C (tolerance: {req.frost_tolerance}°C). Frost days: {frost_days}",
            mitigation=[
                "Frost-tolerant varieties",
                "Adjust planting date",
                "Frost protection (irrigation, heaters)",
                "Wind machines"
            ],
            indicators={"min_temp": tmin, "frost_days": frost_days, "tolerance": req.frost_tolerance}
        ))

        # 4. Flooding / waterlogging risk
        # Use soil drainage and precipitation intensity
        soil_drainage = soil_data.get("drainage", "moderate")
        max_daily_precip = climate_data.get("max_daily_precip", 50)

        if soil_drainage == "poor" and max_daily_precip > 100:
            level = RiskLevel.HIGH
        elif soil_drainage == "poor" or max_daily_precip > 80:
            level = RiskLevel.MODERATE
        else:
            level = RiskLevel.LOW

        risks.append(RiskAssessment(
            risk_type="waterlogging",
            level=level,
            probability=0.3 if level == RiskLevel.HIGH else 0.15,
            impact="Root hypoxia, nutrient loss, disease",
            description=f"Soil drainage: {soil_drainage}. Max daily precip: {max_daily_precip:.0f}mm",
            mitigation=[
                "Drainage improvement",
                "Raised beds",
                "Waterlogging-tolerant varieties",
                "Delayed planting"
            ],
            indicators={"drainage": soil_drainage, "max_daily_precip": max_daily_precip}
        ))

        # 5. Disease pressure risk (simplified - based on humidity)
        rh = climate_data.get("rh_growing", climate_data.get("rh2m_avg", 60))
        rain_days = climate_data.get("rain_days", 50)

        if rh > 80 and rain_days > 80:
            level = RiskLevel.HIGH
        elif rh > 70 and rain_days > 60:
            level = RiskLevel.MODERATE
        else:
            level = RiskLevel.LOW

        risks.append(RiskAssessment(
            risk_type="disease",
            level=level,
            probability=0.4 if level == RiskLevel.HIGH else 0.2,
            impact="Yield loss, quality reduction",
            description=f"Avg humidity: {rh:.0f}%. Rain days: {rain_days}",
            mitigation=[
                "Resistant varieties",
                "Crop rotation",
                "Fungicide program",
                "Canopy management",
                "Forecast-based spraying"
            ],
            indicators={"humidity": rh, "rain_days": rain_days}
        ))

        # 6. Nutrient deficiency risk
        soil_ph = soil_data.get("ph", 7.0)
        soil_om = soil_data.get("organic_matter", 2.0)

        nutrient_risk = 0
        if soil_ph < 5.5 or soil_ph > 8.0:
            nutrient_risk += 1
        if soil_om < 1.5:
            nutrient_risk += 1

        if nutrient_risk >= 2:
            level = RiskLevel.HIGH
        elif nutrient_risk == 1:
            level = RiskLevel.MODERATE
        else:
            level = RiskLevel.LOW

        risks.append(RiskAssessment(
            risk_type="nutrient_deficiency",
            level=level,
            probability=nutrient_risk * 0.3,
            impact="Reduced growth, yield loss",
            description=f"Soil pH: {soil_ph:.1f}. Organic matter: {soil_om:.1f}%",
            mitigation=[
                "Soil testing and targeted fertilization",
                "pH correction (lime/gypsum)",
                "Organic amendments",
                "Cover crops",
                "Precision agriculture"
            ],
            indicators={"ph": soil_ph, "organic_matter": soil_om}
        ))

        return risks

    def estimate_yield_gap(
        self,
        crop: str,
        climate_data: Dict[str, Any],
        soil_data: Dict[str, Any],
        management_level: str = "medium"
    ) -> Dict[str, Any]:
        """
        Estimate yield gap (potential - actual).

        Returns dict with potential, attainable, actual yields and gaps.
        """
        req = self.get_crop_requirements(crop)
        if not req:
            return {"error": "Unknown crop"}

        # Potential yield (climate-limited, no constraints)
        # Simplified: based on radiation and temperature
        solar = climate_data.get("solar_rad_growing", 20)  # MJ/m2/day
        gdd = climate_data.get("gdd", 2000)

        # Rough potential yield estimation
        # Based on biomass production efficiency
        rue = 2.5  # Radiation use efficiency g/MJ
        potential_biomass = solar * 100 * rue / 1000  # t/ha over 100 days
        hi = 0.45  # Harvest index
        potential_yield = potential_biomass * hi

        # Water-limited yield
        water_balance = self.calculate_water_balance(
            crop,
            climate_data.get("daily", []),
            soil_data
        )

        if water_balance.etc > 0:
            water_productivity = req.water_opt / 100  # kg/mm/ha (rough)
            water_limited_yield = min(potential_yield, water_balance.precipitation * water_productivity / 10)
        else:
            water_limited_yield = potential_yield * 0.8

        # Management factor
        mgmt_factors = {"high": 0.9, "medium": 0.7, "low": 0.5}
        mgmt_factor = mgmt_factors.get(management_level, 0.7)

        attainable_yield = water_limited_yield * mgmt_factor

        # Actual yield (would come from farm records)
        # For now estimate as percentage of attainable
        actual_yield = attainable_yield * 0.8  # Assume 80% of attainable

        return {
            "crop": req.name,
            "potential_yield": round(potential_yield, 2),
            "water_limited_yield": round(water_limited_yield, 2),
            "attainable_yield": round(attainable_yield, 2),
            "estimated_actual_yield": round(actual_yield, 2),
            "yield_gap_potential": round(potential_yield - actual_yield, 2),
            "yield_gap_attainable": round(attainable_yield - actual_yield, 2),
            "water_productivity": round(actual_yield / max(water_balance.precipitation, 1) * 1000, 1),
            "management_level": management_level,
            "limiting_factors": self._identify_yield_limits(potential_yield, water_limited_yield, attainable_yield, actual_yield)
        }

    def _identify_yield_limits(
        self, potential: float, water_limited: float, attainable: float, actual: float
    ) -> List[str]:
        """Identify main yield limiting factors"""
        factors = []

        if water_limited < potential * 0.8:
            factors.append("water")
        if attainable < water_limited * 0.9:
            factors.append("management")
        if actual < attainable * 0.9:
            factors.append("technology_adoption")

        if not factors:
            factors.append("near_potential")

        return factors

    def recommend_crops(
        self,
        climate_data: Dict[str, Any],
        soil_data: Dict[str, Any],
        gaez_data: Optional[Dict[str, Any]] = None,
        top_n: int = 5
    ) -> List[SuitabilityScore]:
        """
        Recommend best crops for a location.

        Returns top N crops by suitability score.
        """
        scores = []

        for crop_type in CropType:
            score = self.assess_crop_suitability(
                crop_type.value, climate_data, soil_data, gaez_data
            )
            scores.append(score)

        # Sort by overall score descending
        scores.sort(key=lambda s: s.overall_score, reverse=True)

        return scores[:top_n]


# Singleton
_agricultural_service = None

def get_agricultural_analysis_service() -> AgriculturalAnalysisService:
    global _agricultural_service
    if _agricultural_service is None:
        _agricultural_service = AgriculturalAnalysisService()
    return _agricultural_service