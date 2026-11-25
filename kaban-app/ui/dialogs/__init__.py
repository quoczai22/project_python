"""ui.dialogs: Các cửa sổ pop-up / modal tương tác trong ứng dụng."""
from ui.dialogs.confirm_dialog import ConfirmDialog, xac_nhan
from ui.dialogs.column_dialog import (
    ColumnDialog,
    CotDialog,
    TaoDuAnDialog,
    ThanhVienDuAnDialog,
    TEN_VAI_TRO,
)
from ui.dialogs.task_dialog import TaskDialog, CongViecDialog
from ui.dialogs.doi_mat_khau_dialog import DoiMatKhauDialog
from ui.dialogs.quy_trinh_dialog import QuyTrinhDialog
from ui.dialogs.api_preview_dialog import ApiPreviewDialog
from ui.dialogs.chat_dialog import ChatDialog

__all__ = [
    "ConfirmDialog",
    "xac_nhan",
    "ColumnDialog",
    "CotDialog",
    "TaoDuAnDialog",
    "ThanhVienDuAnDialog",
    "TaskDialog",
    "CongViecDialog",
    "DoiMatKhauDialog",
    "QuyTrinhDialog",
    "ApiPreviewDialog",
    "ChatDialog",
    "TEN_VAI_TRO",
]
