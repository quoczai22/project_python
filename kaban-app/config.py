"""Các hằng số cấu hình dùng chung cho ứng dụng Kanban."""

# Tên các file dữ liệu
TEN_FILE_DU_AN = "du_an.json"
TEN_FILE_DU_LIEU_MOC = "du_lieu_moc.json"

# Danh sách chọn trong Combobox và dùng để kiểm tra dữ liệu công việc.
TRANG_THAI_HOP_LE = ("Cần làm", "Đang làm", "Kiểm tra", "Hoàn thành")
MUC_UU_TIEN_HOP_LE = ("Thấp", "Trung bình", "Cao", "Khẩn")
NHAN_HOP_LE = ("Backend", "Giao diện", "Lỗi", "Tài liệu", "Kiểm thử")


# ---- Lưu trữ & sao lưu (phần Khoa) ----
TEN_FILE_NHAT_KY = "nhat_ky.json"
TEN_THU_MUC_SAO_LUU = "backup"      # nằm cạnh file dữ liệu gốc
SO_BAN_SAO_LUU_TOI_DA = 10          # mỗi file giữ tối đa 10 bản sao lưu mới nhất

# ---- Tài khoản (phần Khoa) ----
MAT_KHAU_TOI_THIEU = 6
MAU_TEN_DANG_NHAP = r"[A-Za-z0-9_]{3,20}"
MAU_EMAIL = r"[A-Za-z0-9._%+\-]+@[A-Za-z0-9\-]+(\.[A-Za-z0-9\-]+)*\.[A-Za-z]{2,}"
