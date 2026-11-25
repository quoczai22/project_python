"""utils.constants: Tập hợp tất cả các hằng số, cấu hình đường dẫn và mã màu của ứng dụng."""
import os

from config import (
    TRANG_THAI_HOP_LE,
    MUC_UU_TIEN_HOP_LE,
    NHAN_HOP_LE,
    TEN_FILE_DU_AN,
    TEN_FILE_DU_LIEU_MOC,
    TEN_FILE_NHAT_KY,
    TEN_THU_MUC_SAO_LUU,
    SO_BAN_SAO_LUU_TOI_DA,
    MAT_KHAU_TOI_THIEU,
    MAU_TEN_DANG_NHAP,
    MAU_EMAIL,
)
from ui.styles.theme import (
    MAU_PALETTE_1, MAU_PALETTE_2, MAU_PALETTE_3, MAU_PALETTE_4, MAU_PALETTE_5,
    MAU_NEN, MAU_CHINH, MAU_CHINH_DAM, MAU_CHINH_NHAT, MAU_NHAN,
    MAU_CHU, MAU_CHU_NHAN, MAU_CHU_PHU, MAU_PLACEHOLDER,
    MAU_THE, MAU_O_NHAP, MAU_COT, MAU_COT_SANG,
    MAU_VIEN, MAU_VIEN_COT, MAU_VIEN_THE,
    MAU_LOI, MAU_HOAN_THANH, MAU_CANH_BAO,
    CORNER_RADIUS,
)

# Đường dẫn thư mục gốc và thư mục tài nguyên
THU_MUC_GOC = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
THU_MUC_DATA = os.path.join(THU_MUC_GOC, "data")
THU_MUC_ASSETS = os.path.join(THU_MUC_GOC, "assets")
THU_MUC_ICONS = os.path.join(THU_MUC_ASSETS, "icons")
THU_MUC_FONTS = os.path.join(THU_MUC_ASSETS, "fonts")
