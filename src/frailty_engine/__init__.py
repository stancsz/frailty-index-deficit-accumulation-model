"""Clinical healthspan and deficit-accumulation engine."""

from .exceptions import InsufficientDataError, ModelUnavailableError, ValidationError
from .derived import calculate_fib_4
from .pipeline import assess
from .training import (
    SurvivalTrainingFrame,
    TrainingQualityReport,
    TrainingSubgroupQuality,
    SurvivalRowSplit,
    build_survival_frame,
    fit_xgb_survival,
    split_survival_rows,
)
from .nhanes import (
    NHANES_BIA_CYCLES,
    NHANESColumnMap,
    NHANESCycleResource,
    build_nhanes_rows,
    build_nhanes_training_frame,
    cycle_resource,
    merge_xpt_files,
    mortality_by_seqn,
    read_public_use_mortality,
    read_xpt,
)
from .validation import (
    OutcomeMetricConstruction,
    OutcomeMetricName,
    OutcomeMetricStatus,
    SubgroupSupportReason,
    SubgroupSupportWarning,
    ValidationReport,
    validate_external_cohort,
    write_calibration_plots,
)
from .seca import SecaScan, SecaTableViewExport, read_seca_tableview_csv
from .release_receipt import ReceiptError, health_to_receipt, receipt_matches_health
from .progress import build_progress_report
from .survey_design import SurveyDesign, SurveyWeightKind

__all__ = [
    "InsufficientDataError",
    "ModelUnavailableError",
    "ValidationError",
    "assess",
    "calculate_fib_4",
    "SurvivalTrainingFrame",
    "TrainingQualityReport",
    "TrainingSubgroupQuality",
    "SurvivalRowSplit",
    "build_survival_frame",
    "fit_xgb_survival",
    "split_survival_rows",
    "NHANES_BIA_CYCLES",
    "NHANESColumnMap",
    "NHANESCycleResource",
    "build_nhanes_rows",
    "build_nhanes_training_frame",
    "cycle_resource",
    "merge_xpt_files",
    "mortality_by_seqn",
    "read_public_use_mortality",
    "read_xpt",
    "SubgroupSupportReason",
    "SubgroupSupportWarning",
    "OutcomeMetricName",
    "OutcomeMetricStatus",
    "OutcomeMetricConstruction",
    "ValidationReport",
    "validate_external_cohort",
    "write_calibration_plots",
    "SecaScan",
    "SecaTableViewExport",
    "read_seca_tableview_csv",
    "ReceiptError",
    "health_to_receipt",
    "receipt_matches_health",
    "build_progress_report",
    "SurveyDesign",
    "SurveyWeightKind",
]

__version__ = "0.1.0"
