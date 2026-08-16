"""Hydrodynamically Zoned LSG — JOH Paper.

Core library for the Journal of Hydrology paper on hydrodynamically zoned
EOF-Gaussian Process learning for rapid flood inundation prediction.
"""

from lsg.baseline_lsg import GlobalLSG
from lsg.zonal_lsg import ZonalLSG
from lsg.zoning import (
    ZoningConfig,
    build_cell_features,
    kmeans_zones,
    rule_based_zones,
)
from lsg.metrics import (
    rmse,
    mae,
    bias,
    contingency_table,
    pod,
    rfa,
    csi,
    extent_metrics,
)

__all__ = [
    "GlobalLSG",
    "ZonalLSG",
    "ZoningConfig",
    "build_cell_features",
    "kmeans_zones",
    "rule_based_zones",
    "rmse",
    "mae",
    "bias",
    "csi",
    "pod",
    "rfa",
    "extent_metrics",
]
__version__ = "1.0.0"
