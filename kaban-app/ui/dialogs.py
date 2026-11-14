"""Tương thích ngược: Re-export toàn bộ Dialogs từ ui.dialogs."""
from ui.dialogs import (
    TaskDialog,
    CongViecDialog,
    ColumnDialog,
    CotDialog,
    TaoDuAnDialog,
    ThanhVienDuAnDialog,
    ConfirmDialog,
    xac_nhan,
)

__all__ = [
    "TaskDialog",
    "CongViecDialog",
    "ColumnDialog",
    "CotDialog",
    "TaoDuAnDialog",
    "ThanhVienDuAnDialog",
    "ConfirmDialog",
    "xac_nhan",
]
