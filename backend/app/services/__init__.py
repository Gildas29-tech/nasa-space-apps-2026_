"""
Services Layer
Orchestration layer combining connectors for agricultural analysis.
"""
from app.services.data_collection import (
    DataCollectionService,
    FarmAnalysisData,
    SourceResult,
    DataSourceStatus,
    get_data_collection_service
)

from app.services.data_validation import (
    DataValidationService,
    ValidationReport,
    ValidationIssue,
    ValidationSeverity,
    DataQuality,
    get_data_validation_service
)

from app.services.geospatial_analysis import (
    GeospatialAnalysisService,
    VegetationIndexResult,
    TimeSeriesPoint,
    NDVITimeSeries,
    get_geospatial_analysis_service
)

from app.services.agricultural_analysis import (
    AgriculturalAnalysisService,
    CropRequirements,
    SuitabilityScore,
    WaterBalanceResult,
    RotationAnalysis,
    RiskAssessment,
    RiskLevel,
    CropType,
    WaterSupply,
    InputLevel,
    get_agricultural_analysis_service,
    CROP_REQUIREMENTS
)

__all__ = [
    # Data Collection
    "DataCollectionService",
    "FarmAnalysisData",
    "SourceResult",
    "DataSourceStatus",
    "get_data_collection_service",

    # Data Validation
    "DataValidationService",
    "ValidationReport",
    "ValidationIssue",
    "ValidationSeverity",
    "DataQuality",
    "get_data_validation_service",

    # Geospatial Analysis
    "GeospatialAnalysisService",
    "VegetationIndexResult",
    "TimeSeriesPoint",
    "NDVITimeSeries",
    "get_geospatial_analysis_service",

    # Agricultural Analysis
    "AgriculturalAnalysisService",
    "CropRequirements",
    "SuitabilityScore",
    "WaterBalanceResult",
    "RotationAnalysis",
    "RiskAssessment",
    "RiskLevel",
    "CropType",
    "WaterSupply",
    "InputLevel",
    "get_agricultural_analysis_service",
    "CROP_REQUIREMENTS",
]