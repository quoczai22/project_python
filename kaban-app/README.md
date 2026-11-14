# Ứng Dụng Quản Lý Công Việc Kanban (Kanban App)

Ứng dụng Quản lý Công việc theo mô hình Kanban được xây dựng bằng Python, hợp nhất hoàn chỉnh giữa **Backend (OOP 4 tính chất, Exception, Transaction Rollback)** và **Frontend (CustomTkinter GUI phẳng 100%, chuẩn Typography & Theme Palette Lavender Pastel)**.

---

## 🚀 1. Khởi Chạy Ứng Dụng (1 File Duy Nhất)

Toàn bộ ứng dụng được khởi chạy thông qua duy nhất file `main.py`:

```bash
# 1. Cài đặt thư viện phụ thuộc
pip install -r requirements.txt

# 2. Khởi chạy ứng dụng (Mở giao diện Đăng nhập)
python main.py

# 3. Khởi chạy nhanh với quyền Quản trị viên (Admin)
python main.py --admin

# 4. Khởi chạy chế độ dòng lệnh Terminal (CLI)
python main.py --cli
```

### Tài khoản mặc định:
- **Quản trị viên:** `admin` / Mật khẩu: `123456`
- **Thành viên:** `khoa` / Mật khẩu: `123456`

---

## 📁 2. Cấu Trúc Thư Mục Đồ Án Chuẩn Hóa

```text
kanban_app/
│
├── assets/                  # Tài nguyên tĩnh (icon, hình ảnh, font chữ...)
│   ├── icons/               # Icon đồ họa phẳng: plus.png, delete.png, edit.png
│   └── fonts/               # Font chữ dự án
│
├── data/                    # Nơi chứa dữ liệu JSON cục bộ
│   ├── kanban_data.json     # Dữ liệu danh sách dự án, cột và task
│   └── default_data.json    # Dữ liệu tài khoản thành viên mẫu
│
├── models/                  # Các lớp (Classes) định nghĩa đối tượng dữ liệu OOP
│   ├── __init__.py
│   ├── task.py              # Class Task (kèm to_dict() và from_dict())
│   ├── column.py            # Class Column (Cột trạng thái & giới hạn WIP)
│   ├── DuAn.py              # Đối tượng Dự án chứa các cột và công việc
│   ├── BinhLuan.py          # Đối tượng Bình luận trên công việc
│   ├── CongViec/            # Kế thừa đa hình: CongViecBase, CongViecThuong, CongViecKhan
│   └── NguoiDung/           # Kế thừa phân quyền: NguoiDungBase, QuanTriVien, ThanhVien
│
├── services/                # Xử lý dữ liệu (JSON / API) và logic nghiệp vụ
│   ├── __init__.py
│   ├── json_handler.py      # Đọc (json.load) và ghi (json.dump) dữ liệu kèm sao lưu
│   ├── kanban_service.py    # Dịch vụ chính (QuanLyKanban) thêm, sửa, xóa, chuyển cột, lọc
│   ├── api_client.py        # Client gửi REST API tích hợp mở rộng
│   └── BoLuuTru/            # Tầng lưu trữ an toàn (BoLuuTruBase, BoLuuTruMock)
│
├── ui/                      # Giao diện người dùng (UI Components - mỗi file < 500 dòng)
│   ├── __init__.py
│   ├── main_window.py       # Cửa sổ chính điều phối Sidebar, Topbar và BoardView
│   ├── board_view.py        # Frame hiển thị Bảng Kanban + Danh sách + Ngăn kéo Hoạt động
│   ├── column_widget.py     # Widget đại diện cho 1 cột trạng thái (WIP, cuộn mượt mà)
│   ├── task_card.py         # Widget đại diện cho 1 thẻ công việc (Task Card)
│   ├── dialogs.py           # Pop-up modal (Thêm/Sửa task, Cột trạng thái, Xác nhận)
│   │
│   ├── components/          # Thành phần giao diện nhỏ (sidebar.py, topbar.py...)
│   ├── dialogs/             # Chi tiết các dialog (task_dialog.py, column_dialog.py...)
│   ├── views/               # Các màn hình lớn (board_view.py, stats_view.py...)
│   └── styles/              # Quản lý màu sắc (theme.py) và kiểu chữ (fonts.py)
│
├── tests/                   # Bộ kiểm thử tự động Unit Tests (58/58 test cases)
│   ├── __init__.py
│   ├── test_oop.py          # Kiểm tra 4 tính chất OOP & xử lý ngoại lệ
│   └── test_luu_tru_tai_khoan.py # Kiểm tra lưu trữ JSON, băm SHA-256, sao lưu/phục hồi
│
├── utils/                   # Các hàm hỗ trợ, tiện ích dùng chung
│   ├── __init__.py
│   ├── constants.py         # Bảng mã màu, kích thước bo góc (corner_radius=0), đường dẫn
│   └── helpers.py           # Hàm format ngày giờ, căn giữa popup, avatar viết tắt
│
├── backup/                  # Thư mục tự động sao lưu dữ liệu khi có thay đổi
├── .gitignore               # Danh sách file/thư mục bỏ qua khi đẩy Git
├── requirements.txt         # Danh sách thư viện Python (customtkinter, pillow...)
├── main.py                  # Entry Point duy nhất khởi chạy ứng dụng
└── README.md                # Tài liệu hướng dẫn sử dụng và báo cáo đồ án
```

---

## 🏛️ 3. Kiến Trúc Backend OOP 4 Tính Chất

1. **Tính Trừu Tượng (Abstraction):**
   - `CongViec(ABC)` quy định các phương thức trừu tượng `@abstractmethod`: `canh_bao()`, `lay_loai_cong_viec()`.
   - `NguoiDung(ABC)` quy định hợp đồng phân quyền: `kiem_tra_quyen_du_an()`, `co_quyen_xoa_cong_viec()`.
   - `BoLuuTruBase(ABC)` quy định hợp đồng lưu trữ, tách rời phụ thuộc (Dependency Inversion).

2. **Tính Kế Thừa (Inheritance):**
   - `CongViecThuong` và `CongViecKhan` kế thừa từ `CongViec`.
   - `QuanTriVien` và `ThanhVien` kế thừa từ `NguoiDung`.

3. **Tính Đóng Gói (Encapsulation):**
   - Thuộc tính nội bộ được bảo vệ (`_ma_cong_viec`, `_mat_khau`, `_muc_uu_tien`...).
   - Kiểm soát truy cập chặt chẽ qua `@property` và `@setter` validation.

4. **Tính Đa Hình (Polymorphism):**
   - Đa hình cảnh báo `cv.canh_bao()` cho từng loại công việc thường và khẩn cấp.
   - Đa hình phân quyền tự động theo vai trò mà không dùng rẽ nhánh `if-else`.

---

## 🛡️ 4. Toàn Vẹn Dữ Liệu & Xử Lý Ngoại Lệ

- **Transaction Rollback:** Tự động hoàn tác trạng thái trên RAM nếu quá trình ghi đĩa JSON gặp sự cố.
- **Tự động sao lưu & phục hồi:** Lưu lịch sử các bản sao lưu trong thư mục `backup/`, tự động khôi phục nếu file JSON bị hỏng hoặc mất dữ liệu.
- **Hệ thống Exception chuyên biệt:** `DuLieuKhongHopLeError`, `KhongCoQuyenError`, `XungDotDuLieuError`, `LoiLuuTruError`...

---

## 🧪 5. Kiểm Thử Hệ Thống (Unit Tests)

Chạy bộ kiểm thử tự động toàn diện:
```bash
python -m unittest discover tests -v
```
*(58/58 test cases đều đạt trạng thái PASS)*
