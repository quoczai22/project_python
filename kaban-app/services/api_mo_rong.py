"""Nguồn API mẫu và tính hạn làm việc; lỗi mạng trả về để UI hiển thị."""
from datetime import date, timedelta
from services.quote_api import lay_du_lieu_api


def lay_ngay_le_viet_nam(nam):
    if not isinstance(nam, int) or not 2026 <= nam <= 2030:
        return None, "Tallyfy chỉ cung cấp dữ liệu từ 2026 đến 2030"
    data, loi = lay_du_lieu_api(f"https://tallyfy.com/national-holidays/api/VN/{nam}.json")
    if loi:
        return None, loi
    if not isinstance(data, dict) or not isinstance(data.get("holidays"), list):
        return None, "Dữ liệu ngày lễ không hợp lệ"
    try:
        return {date.fromisoformat(muc["date"]) for muc in data["holidays"]}, None
    except (KeyError, TypeError, ValueError):
        return None, "Dữ liệu ngày lễ không hợp lệ"


def cong_ngay_lam_viec(ngay_bat_dau, so_ngay, ngay_le=()):
    """Tính hạn sau N ngày làm việc, bỏ qua thứ Bảy, Chủ nhật và ngày lễ."""
    if not isinstance(ngay_bat_dau, date) or not isinstance(so_ngay, int) or so_ngay < 0:
        raise ValueError("Ngày bắt đầu hoặc số ngày làm việc không hợp lệ")
    ngay = ngay_bat_dau
    ngay_le = set(ngay_le)
    for _ in range(so_ngay):
        ngay += timedelta(days=1)
        while ngay.weekday() >= 5 or ngay in ngay_le:
            ngay += timedelta(days=1)
    return ngay


def lay_cau_dong_vien():
    data, loi = lay_du_lieu_api("https://dummyjson.com/quotes/random")
    if loi:
        return None, loi
    if not isinstance(data, dict) or not isinstance(data.get("quote"), str):
        return None, "Dữ liệu câu trích dẫn không hợp lệ"
    return {"noi_dung": data["quote"], "tac_gia": str(data.get("author", ""))}, None


def lay_nguoi_dung_mau():
    data, loi = lay_du_lieu_api("https://jsonplaceholder.typicode.com/users")
    if loi:
        return None, loi
    if not isinstance(data, list):
        return None, "Dữ liệu người dùng không hợp lệ"
    ket_qua = []
    for muc in data[:10]:
        if isinstance(muc, dict) and isinstance(muc.get("name"), str) and isinstance(muc.get("email"), str):
            ket_qua.append({"ten_dang_nhap": f"demo_{muc.get('id')}",
                            "ho_ten": muc["name"], "email": muc["email"]})
    return ket_qua, None
