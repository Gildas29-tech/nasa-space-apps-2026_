"""
Data Validation Service
Quality checks and validation for collected agricultural data.
"""
from datetime import date, datetime
from typing import Optional, Dict, Any, List, Tuple
from dataclasses import dataclass, field
from enum import Enum
import numpy as np


class ValidationSeverity(str, Enum):
    """Severity of validation issue"""
    INFO = "info"
    WARNING = "warning"
    ERROR = "error"
    CRITICAL = "critical"


class DataQuality(str, Enum):
    """Overall data quality assessment"""
    EXCELLENT = "excellent"
    GOOD = "good"
    FAIR = "fair"
    POOR = "poor"
    UNUSABLE = "unusable"


@dataclass
class ValidationIssue:
    """Single validation issue"""
    field: str
    severity: ValidationSeverity
    message: str
    expected: Any = None
    actual: Any = None
    suggestion: Optional[str] = None


@dataclass
class ValidationReport:
    """Validation report for a data source"""
    source: str
    quality: DataQuality
    issues: List[ValidationIssue] = field(default_factory=list)
    completeness: float = 1.0  # 0-1
    consistency_score: float = 1.0  # 0-1
    temporal_coverage: float = 1.0  # 0-1
    spatial_coverage: float = 1.0  # 0-1

    def add_issue(self, field: str, severity: ValidationSeverity, message: str,
                  expected: Any = None, actual: Any = None, suggestion: str = None):
        self.issues.append(ValidationIssue(
            field=field, severity=severity, message=message,
            expected=expected, actual=actual, suggestion=suggestion
        ))

    def has_errors(self) -> bool:
        return any(i.severity in (ValidationSeverity.ERROR, ValidationSeverity.CRITICAL)
                   for i in self.issues)

    def has_warnings(self) -> bool:
        return any(i.severity == ValidationSeverity.WARNING for i in self.issues)

    def get_summary(self) -> Dict[str, Any]:
        return {
            "source": self.source,
            "quality": self.quality.value,
            "completeness": round(self.completeness, 2),
            "consistency": round(self.consistency_score, 2),
            "temporal_coverage": round(self.temporal_coverage, 2),
            "spatial_coverage": round(self.spatial_coverage, 2),
            "issues_count": len(self.issues),
            "errors": sum(1 for i in self.issues if i.severity in (ValidationSeverity.ERROR, ValidationSeverity.CRITICAL)),
            "warnings": sum(1 for i in self.issues if i.severity == ValidationSeverity.WARNING),
            "info": sum(1 for i in self.issues if i.severity == ValidationSeverity.INFO),
        }


class DataValidationService:
    """
    Validates and assesses quality of agricultural data from various sources.

    Performs:
    - Completeness checks (missing values, temporal gaps)
    - Consistency checks (outliers, physical limits)
    - Temporal coverage assessment
    - Spatial coverage assessment
    - Cross-source validation where applicable
    """

    # Physical limits for climate variables
    CLIMATE_LIMITS = {
        "T2M": {"min": -50, "max": 60, "unit": "°C"},          # Temperature
        "T2M_MAX": {"min": -50, "max": 60, "unit": "°C"},
        "T2M_MIN": {"min": -50, "max": 60, "unit": "°C"},
        "PRECTOTCORR": {"min": 0, "max": 500, "unit": "mm/day"},  # Precipitation
        "RH2M": {"min": 0, "max": 100, "unit": "%"},            # Relative humidity
        "ALLSKY_SFC_SW_DWN": {"min": 0, "max": 40, "unit": "MJ/m²/day"},  # Solar radiation
        "WS2M": {"min": 0, "max": 50, "unit": "m/s"},           # Wind speed
    }

    # NDVI limits
    NDVI_LIMITS = {"min": -1, "max": 1}

    # Soil moisture limits (volumetric)
    SM_LIMITS = {"min": 0, "max": 0.6, "unit": "m³/m³"}

    def __init__(self):
        pass

    def validate_nasa_power(self, data: Any, start_date: date, end_date: date) -> ValidationReport:
        """Validate NASA POWER climate data"""
        report = ValidationReport(source="NASA POWER", quality=DataQuality.EXCELLENT)

        if not data:
            report.quality = DataQuality.UNUSABLE
            report.add_issue("data", ValidationSeverity.CRITICAL, "No data returned")
            return report

        # Check if response has parameters
        if not hasattr(data, 'parameters') or not data.parameters:
            report.quality = DataQuality.UNUSABLE
            report.add_issue("parameters", ValidationSeverity.CRITICAL, "No parameters in response")
            return report

        expected_params = list(self.CLIMATE_LIMITS.keys())
        found_params = list(data.parameters.keys()) if hasattr(data.parameters, 'keys') else []

        # Check completeness
        missing_params = [p for p in expected_params if p not in found_params]
        if missing_params:
            report.completeness = 1 - (len(missing_params) / len(expected_params))
            for p in missing_params:
                report.add_issue(
                    f"parameter.{p}", ValidationSeverity.WARNING,
                    f"Missing expected parameter: {p}",
                    expected="present", actual="missing",
                    suggestion=f"Check NASA POWER API availability for {p}"
                )

        # Validate each parameter
        for param_name, param_data in data.parameters.items():
            if param_name not in self.CLIMATE_LIMITS:
                continue

            limits = self.CLIMATE_LIMITS[param_name]
            values = param_data.values if hasattr(param_data, 'values') else {}

            if not values:
                report.add_issue(
                    f"parameter.{param_name}.values", ValidationSeverity.WARNING,
                    f"No values for {param_name}",
                    suggestion="Check date range and API response"
                )
                continue

            # Check temporal coverage
            expected_days = (end_date - start_date).days + 1
            actual_days = len(values)
            report.temporal_coverage = min(actual_days / expected_days, 1.0)

            if actual_days < expected_days * 0.9:
                report.add_issue(
                    f"parameter.{param_name}.temporal", ValidationSeverity.WARNING,
                    f"Temporal gap: {actual_days}/{expected_days} days",
                    expected=expected_days, actual=actual_days,
                    suggestion="Some days may be missing from API"
                )

            # Validate value ranges
            for date_str, value in values.items():
                if value is None:
                    continue
                try:
                    val = float(value)
                    if val < limits["min"] or val > limits["max"]:
                        report.consistency_score *= 0.95
                        report.add_issue(
                            f"parameter.{param_name}.range", ValidationSeverity.WARNING,
                            f"Value out of physical range: {val} {limits['unit']} on {date_str}",
                            expected=f"{limits['min']}-{limits['max']} {limits['unit']}", actual=f"{val} {limits['unit']}",
                            suggestion="Possible API error or extreme weather event"
                        )
                except (ValueError, TypeError):
                    report.add_issue(
                        f"parameter.{param_name}.type", ValidationSeverity.ERROR,
                        f"Non-numeric value: {value}",
                        expected="number", actual=type(value).__name__
                    )

        # Overall quality assessment
        report.quality = self._assess_quality(report)
        return report

    def validate_gpm_precipitation(self, data: Any, start_date: date, end_date: date) -> ValidationReport:
        """Validate GPM precipitation data"""
        report = ValidationReport(source="NASA GPM IMERG", quality=DataQuality.EXCELLENT)

        if not data or not hasattr(data, 'data') or not data.data:
            report.quality = DataQuality.UNUSABLE
            report.add_issue("data", ValidationSeverity.CRITICAL, "No precipitation data")
            return report

        expected_days = (end_date - start_date).days + 1
        actual_days = len(data.data)
        report.temporal_coverage = min(actual_days / expected_days, 1.0)

        if actual_days == 0:
            report.quality = DataQuality.UNUSABLE
            report.add_issue("data", ValidationSeverity.CRITICAL, "Empty precipitation dataset")
            return report

        # Check for reasonable values
        precip_values = [d.precipitation for d in data.data if d.precipitation is not None]
        if precip_values:
            max_precip = max(precip_values)
            if max_precip > 500:  # mm/day - extreme
                report.consistency_score *= 0.9
                report.add_issue(
                    "precipitation.max", ValidationSeverity.WARNING,
                    f"Extreme precipitation value: {max_precip} mm/day",
                    suggestion="Verify with ground stations"
                )

        report.quality = self._assess_quality(report)
        return report

    def validate_smap_soil_moisture(self, data: Any, start_date: date, end_date: date) -> ValidationReport:
        """Validate SMAP soil moisture data"""
        report = ValidationReport(source="NASA SMAP", quality=DataQuality.EXCELLENT)

        if not data or not hasattr(data, 'data') or not data.data:
            report.quality = DataQuality.UNUSABLE
            report.add_issue("data", ValidationSeverity.CRITICAL, "No soil moisture data")
            return report

        expected_days = (end_date - start_date).days + 1
        actual_days = len(data.data)
        report.temporal_coverage = min(actual_days / expected_days, 1.0)

        # Validate soil moisture values
        for point in data.data:
            for field in ["surface_soil_moisture", "root_zone_soil_moisture"]:
                value = getattr(point, field, None)
                if value is not None:
                    if value < self.SM_LIMITS["min"] or value > self.SM_LIMITS["max"]:
                        report.consistency_score *= 0.95
                        report.add_issue(
                            f"{field}.range", ValidationSeverity.WARNING,
                            f"Soil moisture out of range: {value} m³/m³",
                            expected=f"{self.SM_LIMITS['min']}-{self.SM_LIMITS['max']} m³/m³", actual=str(value)
                        )

        report.quality = self._assess_quality(report)
        return report

    def validate_sentinel2(self, data: Any, start_date: date, end_date: date) -> ValidationReport:
        """Validate Sentinel-2 data availability"""
        report = ValidationReport(source="Sentinel-2", quality=DataQuality.EXCELLENT)

        if not data:
            report.quality = DataQuality.UNUSABLE
            report.add_issue("data", ValidationSeverity.CRITICAL, "No Sentinel-2 data")
            return report

        items_count = data.get("items_count", 0)
        available_dates = data.get("available_dates", [])

        if items_count == 0:
            report.quality = DataQuality.POOR
            report.add_issue("items", ValidationSeverity.WARNING,
                           "No Sentinel-2 images found for period",
                           suggestion="Increase cloud cover threshold or expand date range")
            report.completeness = 0.0
        elif items_count < 5:
            report.quality = DataQuality.FAIR
            report.add_issue("items", ValidationSeverity.INFO,
                           f"Only {items_count} images available",
                           suggestion="Consider Landsat for historical coverage")

        # Check temporal distribution
        if available_dates:
            dates = [d.get("date") for d in available_dates if d.get("date")]
            if dates:
                # Check for gaps > 30 days
                sorted_dates = sorted(dates)
                max_gap = 0
                for i in range(1, len(sorted_dates)):
                    d1 = datetime.fromisoformat(sorted_dates[i-1]).date()
                    d2 = datetime.fromisoformat(sorted_dates[i]).date()
                    gap = (d2 - d1).days
                    max_gap = max(max_gap, gap)

                if max_gap > 30:
                    report.add_issue(
                        "temporal.gap", ValidationSeverity.WARNING,
                        f"Maximum temporal gap: {max_gap} days",
                        suggestion="Consider supplementing with Landsat"
                    )

        report.quality = self._assess_quality(report)
        return report

    def validate_landsat(self, data: Any, start_date: date, end_date: date) -> ValidationReport:
        """Validate Landsat data availability"""
        report = ValidationReport(source="Landsat", quality=DataQuality.EXCELLENT)

        if not data:
            report.quality = DataQuality.UNUSABLE
            report.add_issue("data", ValidationSeverity.CRITICAL, "No Landsat data")
            return report

        items_count = data.get("items_count", 0)
        available_dates = data.get("available_dates", [])

        if items_count == 0:
            report.quality = DataQuality.POOR
            report.add_issue("items", ValidationSeverity.WARNING,
                           "No Landsat images found for period")
            report.completeness = 0.0

        report.quality = self._assess_quality(report)
        return report

    def validate_gaez(self, data: Any) -> ValidationReport:
        """Validate FAO GAEZ data"""
        report = ValidationReport(source="FAO GAEZ", quality=DataQuality.EXCELLENT)

        if not data:
            report.quality = DataQuality.UNUSABLE
            report.add_issue("data", ValidationSeverity.CRITICAL, "No GAEZ data")
            return report

        crops = data.get("crops", [])
        if not crops:
            report.quality = DataQuality.POOR
            report.add_issue("crops", ValidationSeverity.WARNING,
                           "No crop suitability data available",
                           suggestion="Check if GAEZ rasters are downloaded")
            report.completeness = 0.0
        else:
            # Check for valid suitability indices
            valid_crops = 0
            for crop in crops:
                suit = crop.get("suitability")
                if suit is not None and 0 <= suit <= 100:
                    valid_crops += 1
                else:
                    report.add_issue(
                        f"crop.{crop.get('crop', 'unknown')}.suitability",
                        ValidationSeverity.WARNING,
                        f"Invalid or missing suitability index: {suit}"
                    )

            report.completeness = valid_crops / len(crops) if crops else 0

        # Check agro-climatic indicators
        agro = data.get("agro_climatic", {})
        if not agro:
            report.add_issue("agro_climatic", ValidationSeverity.INFO,
                           "No agro-climatic indicators available")

        # Check soil constraints
        soil = data.get("soil_constraints", {})
        if not soil:
            report.add_issue("soil_constraints", ValidationSeverity.INFO,
                           "No soil/terrain constraints available")

        report.quality = self._assess_quality(report)
        return report

    def _assess_quality(self, report: ValidationReport) -> DataQuality:
        """Assess overall quality based on metrics"""
        # Weighted scoring
        score = (
            report.completeness * 0.3 +
            report.consistency_score * 0.3 +
            report.temporal_coverage * 0.2 +
            report.spatial_coverage * 0.2
        )

        # Penalize for errors
        error_count = sum(1 for i in report.issues
                         if i.severity in (ValidationSeverity.ERROR, ValidationSeverity.CRITICAL))
        if error_count > 0:
            score *= max(0.5, 1 - error_count * 0.1)

        # Penalize for warnings
        warning_count = sum(1 for i in report.issues if i.severity == ValidationSeverity.WARNING)
        if warning_count > 0:
            score *= max(0.7, 1 - warning_count * 0.05)

        if score >= 0.9:
            return DataQuality.EXCELLENT
        elif score >= 0.75:
            return DataQuality.GOOD
        elif score >= 0.5:
            return DataQuality.FAIR
        elif score >= 0.25:
            return DataQuality.POOR
        else:
            return DataQuality.UNUSABLE

    def validate_cross_sources(self, reports: Dict[str, ValidationReport]) -> ValidationReport:
        """Cross-validate between data sources"""
        cross_report = ValidationReport(source="Cross-Source Validation", quality=DataQuality.EXCELLENT)

        # Check if climate and precipitation both available
        has_climate = "NASA POWER" in reports and reports["NASA POWER"].quality != DataQuality.UNUSABLE
        has_gpm = "NASA GPM IMERG" in reports and reports["NASA GPM IMERG"].quality != DataQuality.UNUSABLE
        has_smap = "NASA SMAP" in reports and reports["NASA SMAP"].quality != DataQuality.UNUSABLE

        if has_climate and has_gpm:
            cross_report.add_issue("climate_precip", ValidationSeverity.INFO,
                                 "Both NASA POWER and GPM precipitation available - cross-validation possible")

        if has_climate and has_smap:
            cross_report.add_issue("climate_soil", ValidationSeverity.INFO,
                                 "Climate and soil moisture available - water balance analysis possible")

        # Check satellite coverage
        has_sentinel = "Sentinel-2" in reports and reports["Sentinel-2"].quality != DataQuality.UNUSABLE
        has_landsat = "Landsat" in reports and reports["Landsat"].quality != DataQuality.UNUSABLE

        if has_sentinel and has_landsat:
            cross_report.add_issue("satellite", ValidationSeverity.INFO,
                                 "Both Sentinel-2 and Landsat available - long-term NDVI possible")
        elif has_sentinel:
            cross_report.add_issue("satellite", ValidationSeverity.INFO,
                                 "Sentinel-2 available - high-res NDVI (2015+)")
        elif has_landsat:
            cross_report.add_issue("satellite", ValidationSeverity.INFO,
                                 "Landsat available - historical NDVI (1984+)")
        else:
            cross_report.add_issue("satellite", ValidationSeverity.WARNING,
                                 "No satellite data available - vegetation monitoring limited")

        # Check GAEZ
        has_gaez = "FAO GAEZ" in reports and reports["FAO GAEZ"].quality != DataQuality.UNUSABLE
        if has_gaez:
            cross_report.add_issue("gaez", ValidationSeverity.INFO,
                                 "GAEZ data available - crop suitability analysis possible")
        else:
            cross_report.add_issue("gaez", ValidationSeverity.WARNING,
                                 "No GAEZ data - crop suitability analysis unavailable")

        cross_report.quality = self._assess_quality(cross_report)
        return cross_report


# Singleton
_validation_service = None

def get_data_validation_service() -> DataValidationService:
    global _validation_service
    if _validation_service is None:
        _validation_service = DataValidationService()
    return _validation_service