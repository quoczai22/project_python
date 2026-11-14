"""utils.helpers: Các hàm tiện ích dùng chung trong toàn bộ hệ thống."""
import re
import uuid
from datetime import datetime, date


def can_giua(cua_so, rong=None, cao=None):
    """Đặt cửa sổ vào chính giữa màn hình làm việc."""
    cua_so.update_idletasks()
    w = rong or cua_so.winfo_width()
    h = cao or cua_so.winfo_height()
    sw = cua_so.winfo_screenwidth()
    sh = cua_so.winfo_screenheight()
    x = max((sw - w) // 2, 0)
    y = max((sh - h) // 2, 0)
    cua_so.geometry(f"{w}x{h}+{x}+{y}")


def tao_chu_viet_tat(ho_ten: str) -> str:
    """Tạo chữ cái viết tắt (2 ký tự) đại diện cho avatar từ họ và tên."""
    if not ho_ten:
        return "??"
    cac_tu = [t for t in ho_ten.strip().split() if t]
    if not cac_tu:
        return "??"
    if len(cac_tu) == 1:
        return cac_tu[0][:2].upper()
    return (cac_tu[0][0] + cac_tu[-1][0]).upper()


def tao_ma_ngau_nhien(tien_to="ID") -> str:
    """Tạo mã định danh ngẫu nhiên kèm tiền tố."""
    return f"{tien_to}-{uuid.uuid4().hex[:6].upper()}"


def dinh_dang_ngay(gia_tri_ngay) -> str:
    """Format ngày tháng sang định dạng chuẩn YYYY-MM-DD."""
    if isinstance(gia_tri_ngay, (datetime, date)):
        return gia_tri_ngay.strftime("%Y-%m-%d")
    return str(gia_tri_ngay or "")


def kiem_tra_dinh_dang_ngay(chuoi_ngay: str) -> bool:
    """Kiểm tra xem chuỗi có đúng định dạng ngày YYYY-MM-DD hay không."""
    if not re.fullmatch(r"\d{4}-\d{2}-\d{2}", chuoi_ngay):
        return False
    try:
        datetime.strptime(chuoi_ngay, "%Y-%m-%d")
        return True
    except ValueError:
        return False
