"""Khung tích hợp API bên ngoài cho phần việc của Phú.

Truyền URL API JSON đã được nhóm chọn; hàm chỉ lấy và chuẩn hóa dữ liệu.
Việc quyết định nguồn API, cách hiển thị và thời điểm lưu do Phú hoàn thiện.
"""

import json
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen


def lay_du_lieu_api(url, timeout=5):
    """Trả về (dữ liệu JSON, lỗi); lỗi kết nối không làm dừng ứng dụng."""
    if not isinstance(url, str) or not url.startswith(("https://", "http://")):
        return None, "URL API phải bắt đầu bằng http:// hoặc https://"
    if timeout <= 0:
        return None, "Thời gian chờ phải lớn hơn 0"
    try:
        with urlopen(Request(url, headers={"User-Agent": "KanbanApp/1.0"}), timeout=timeout) as response:
            return json.load(response), None
    except (HTTPError, URLError, TimeoutError, ValueError, OSError) as loi:
        return None, str(loi)


def lay_va_luu_du_lieu_api(url, duong_dan, bo_luu_tru, timeout=5):
    """Lấy JSON từ API và chuyển việc ghi file cho tầng lưu trữ của Khoa."""
    du_lieu, loi = lay_du_lieu_api(url, timeout)
    if loi:
        return None, loi
    try:
        da_luu = bo_luu_tru.ghi_json(duong_dan, du_lieu)
        if da_luu is False:
            return None, "Không lưu được dữ liệu API vào JSON"
        return du_lieu, None
    except (OSError, ValueError, TypeError) as loi:
        return None, str(loi)
