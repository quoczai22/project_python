"""Các hằng số cấu hình dùng chung cho ứng dụng Kanban."""
import os
import sys

# Thư mục gốc của ứng dụng: cạnh file .exe khi đã đóng gói, cạnh config.py khi chạy từ mã nguồn.
# Nhờ vậy đường dẫn dữ liệu đúng dù chạy lệnh ở thư mục nào (khớp với main.py khi đóng gói).
if getattr(sys, "frozen", False):
    THU_MUC_GOC = os.path.dirname(os.path.abspath(sys.executable))
else:
    THU_MUC_GOC = os.path.dirname(os.path.abspath(__file__))

# Tên các file dữ liệu (lưu trữ tập trung trong thư mục data/)
THU_MUC_DATA = os.path.join(THU_MUC_GOC, "data")
TEN_FILE_DU_AN = os.path.join(THU_MUC_DATA, "du_an.json")
TEN_FILE_DU_LIEU_MOC = os.path.join(THU_MUC_DATA, "du_lieu_moc.json")
TEN_FILE_NHAT_KY = os.path.join(THU_MUC_DATA, "nhat_ky.json")

# Danh sách chọn trong Combobox và dùng để kiểm tra dữ liệu công việc.
TRANG_THAI_HOP_LE = ("Cần làm", "Đang làm", "Kiểm tra", "Hoàn thành", "Đã hủy")
MUC_UU_TIEN_HOP_LE = ("Thấp", "Trung bình", "Cao", "Khẩn")
NHAN_HOP_LE = ("Backend", "Giao diện", "Lỗi", "Tài liệu", "Kiểm thử")

# ---- Lưu trữ & sao lưu ----
TEN_THU_MUC_SAO_LUU = "backup"      # nằm cạnh file dữ liệu gốc trong data/
SO_BAN_SAO_LUU_TOI_DA = 10          # mỗi file giữ tối đa 10 bản sao lưu mới nhất

# ---- Tài khoản ----
MAT_KHAU_TOI_THIEU = 6
MAU_TEN_DANG_NHAP = r"[A-Za-z0-9_]{3,20}"
MAU_EMAIL = r"[A-Za-z0-9._%+\-]+@[A-Za-z0-9\-]+(\.[A-Za-z0-9\-]+)*\.[A-Za-z]{2,}"

# ---- Mã định danh và ngày tháng (dùng với re.fullmatch) ----
MAU_MA_CONG_VIEC = r"CV-(\d+)"      # nhóm 1 = số thứ tự, ví dụ CV-012 -> "012"
MAU_MA_DU_AN = r"DA-(\d+)"          # ví dụ DA-003 -> "003"
MAU_NGAY = r"\d{4}-\d{2}-\d{2}"     # dạng YYYY-MM-DD
DINH_DANG_NGAY = "%Y-%m-%d"         # dùng cho datetime.strptime / strftime

# ---- API bên ngoài (nhập công việc mẫu) ----
# Nguồn dữ liệu: DummyJSON Todos - https://dummyjson.com/docs/todos (miễn phí, không cần khóa API)
URL_API_TODOS = "https://dummyjson.com/todos"
TEN_FILE_API = os.path.join(THU_MUC_DATA, "api_todos.json")   # nơi lưu dữ liệu đã làm sạch
TIMEOUT_API = 5            # giây; quá thời gian thì báo lỗi, không treo ứng dụng
SO_VIEC_API_TOI_DA = 10    # số công việc tối đa cho mỗi lần nhập
