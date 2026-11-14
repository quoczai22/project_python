"""Định nghĩa hệ thống kiểu chữ và cỡ chữ chuẩn dùng chung cho toàn bộ ứng dụng."""
import tkinter.font as tkfont

# Phông chữ giao diện chính (Segoe UI ưu tiên số 1 trên Windows, fallback Arial)
FONT_FAMILY = "Segoe UI"

def font_family(size: int = 13, weight: str = "normal") -> tuple:
    """Trả về tuple font với font family chuẩn của hệ thống, size tối thiểu 11pt."""
    size_an_toan = max(11, size)
    return (FONT_FAMILY, size_an_toan, weight)

# Khai báo kiểu chữ chuẩn dùng chung toàn bộ app (tất cả size >= 11pt)
FONT_TIEU_DE = (FONT_FAMILY, 15, "bold")      # Tiêu đề form, header nổi bật
FONT_CHAO_MUNG = (FONT_FAMILY, 15, "bold")    # Tiêu đề chào mừng / Header dự án
FONT_PHU_DE = (FONT_FAMILY, 13)               # Phụ đề, nhãn phụ form
FONT_CHUAN = (FONT_FAMILY, 13)                # Văn bản thông thường, mô tả
FONT_DAM = (FONT_FAMILY, 13, "bold")          # Văn bản nhấn mạnh, nút chính
FONT_NHO = (FONT_FAMILY, 11)                  # Nhãn nhỏ, ngày tháng, thông tin phụ
FONT_NHO_DAM = (FONT_FAMILY, 11, "bold")      # Nhãn badge, cột tiêu đề, nút nhỏ
FONT_KPI = (FONT_FAMILY, 20, "bold")          # Số liệu thống kê lớn trên thẻ KPI
