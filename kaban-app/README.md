# Hệ Thống Quản Lý Công Việc Kanban (Kanban App Backend)

Hệ thống Backend cho ứng dụng Quản lý Công việc theo mô hình Kanban được xây dựng bằng Python, áp dụng chuẩn mực **4 tính chất Lập trình Hướng đối tượng (OOP)**, **Hệ thống Xử lý ngoại lệ (Custom Exceptions)** và **Cơ chế Toàn vẹn dữ liệu (Transaction Rollback)**.

---

## 🏛️ 1. Kiến Trúc 4 Tính Chất OOP

### 1.1. Tính Trừu Tượng (Abstraction)
* **`CongViec(ABC)`** ([models/CongViec/CongViecBase.py](models/CongViec/CongViecBase.py)):
  - Định nghĩa giao diện chung cho mọi công việc qua module `abc.ABC`.
  - Quy định các phương thức trừu tượng `@abstractmethod`: `canh_bao()`, `lay_loai_cong_viec()`.
  - Ngăn chặn khởi tạo trực tiếp instance chưa hoàn thiện.
* **`NguoiDung(ABC)`** ([models/NguoiDung/NguoiDungBase.py](models/NguoiDung/NguoiDungBase.py)):
  - Quy định hợp đồng kiểm tra quyền truy cập: `kiem_tra_quyen_du_an()`, `kiem_tra_quyen_cong_viec()`, `co_quyen_xoa_cong_viec()`.
* **`BoLuuTruBase(ABC)`** ([services/BoLuuTru/BoLuuTruBase.py](services/BoLuuTru/BoLuuTruBase.py)):
  - Quy định giao diện tầng lưu trữ (`doc_json`, `ghi_json`, `ghi_nhat_ky`, `doc_danh_sach_thanh_vien`), áp dụng nguyên lý Dependency Inversion (DIP).

### 1.2. Tính Kế Thừa (Inheritance)
* **Phân cấp Công việc:**
  - `CongViecThuong` kế thừa `CongViec`, tái sử dụng logic tính ngày, cập nhật trạng thái.
  - `CongViecKhan` kế thừa `CongViec`, tái sử dụng `super().__init__(...)` và mở rộng xử lý khẩn cấp.
* **Phân cấp Người dùng:**
  - `ThanhVien` và `QuanTriVien` cùng kế thừa từ `NguoiDung`.
* **Phân cấp Lưu trữ:**
  - `BoLuuTruMock` kế thừa từ `BoLuuTruBase`.

### 1.3. Tính Đóng Gói (Encapsulation)
* Dữ liệu nội bộ được bảo vệ với tiền tố `_` (`_ma_cong_viec`, `_ma_du_an`, `_mat_khau`, `_muc_uu_tien`,...).
* Kiểm soát truy xuất và gán giá trị hợp lệ qua `@property` & `@setter`:
  - `ma_cong_viec` / `ma_du_an`: Kiểm tra regex hợp lệ (`CV-xxx`, `DA-xxx`).
  - `ngay_ket_thuc`: Đảm bảo không trước `ngay_bat_dau`.
  - `CongViecKhan`: Đóng gói mức ưu tiên luôn luôn là `"Khẩn"`.
  - `NguoiDung`: Mật khẩu được ẩn, xác thực qua `kiem_tra_mat_khau()` và `doi_mat_khau()`.

### 1.4. Tính Đa Hình (Polymorphism)
* **Đa hình Cảnh báo (`canh_bao()`):**
  - Duyệt danh sách công việc trong dự án cùng gọi `cv.canh_bao()`.
  - `CongViecThuong`: Phản hồi thời hạn thông thường.
  - `CongViecKhan`: Phản hồi theo các cấp độ khẩn cấp (*QUÁ HẠN*, *KHẨN CẤP*, *CẢNH BÁO ĐỎ*).
* **Đa hình Phân quyền:**
  - `QuanLyKanban` gọi `nguoi_dung.kiem_tra_quyen_du_an(du_an)` hoặc `nguoi_dung.co_quyen_xoa_cong_viec()`.
  - `QuanTriVien` tự động cấp quyền toàn phần; `ThanhVien` tự động kiểm tra phạm vi được phân công mà không cần dùng câu lệnh `if-else` kiểm tra loại đối tượng.
* **Factory Method Đa hình:** `CongViec.from_dict()` và `NguoiDung.from_dict()` tự động phân tích dữ liệu và khởi tạo đúng lớp đối tượng con cụ thể.

---

## 🛡️ 2. Hệ Thống Xử Lý Ngoại Lệ & Toàn Vẹn Dữ Liệu

### 2.1. Cây Phân Cấp Ngoại Lệ ([exceptions.py](exceptions.py))
Toàn bộ thông báo lỗi dùng `print()` trước đây đã được thay thế hoàn toàn bằng việc ném ngoại lệ (`raise`):
```text
KanbanException (Lớp cơ sở)
├── DuLieuKhongHopLeError  (Validation Error - mã sai định dạng, ngày sai logic)
├── KhongTimThayError      (Not Found Error - không tìm thấy dự án, công việc)
├── KhongCoQuyenError      (Forbidden Error - người dùng không đủ quyền)
├── XungDotDuLieuError     (Conflict Error - trùng mã ID)
├── XacThucThatBaiError    (Authentication Error - sai mật khẩu)
└── LoiLuuTruError         (Storage/IO Error - file lỗi hoặc hỏng đĩa)
```

### 2.2. Cơ Chế Transaction Rollback
Khi các thao tác ghi file JSON gặp sự cố (mạng, quyền ghi đĩa, mất điện), hệ thống tự động hoàn tác trạng thái trong bộ nhớ RAM về đúng ban đầu:
- **Tạo dự án / công việc:** Tự động gỡ bỏ khỏi danh sách RAM nếu lưu thất bại.
- **Cập nhật công việc:** Lưu lại `snapshot` cũ, phục hồi ngay nếu lưu file thất bại.
- **Xóa dự án / công việc:** Giữ lại tham chiếu đối tượng, tự động thêm lại vào danh sách nếu lưu thất bại.
- **Chuyển cột:** Khôi phục `trang_thai_cu` nếu ghi nhật ký hoặc lưu file thất bại.

### 2.3. Hệ Thống Logging ([logger.py](logger.py))
Ứng dụng sử dụng module `logging` chuẩn của Python với định dạng chuyên nghiệp:
`[YYYY-MM-DD HH:MM:SS] [LEVEL] [KanbanApp]: Message`

---

## 📁 3. Cấu Trúc Thư Mục Dự Án

```text
kaban-app/
├── config.py                        # Cấu hình hằng số ứng dụng
├── exceptions.py                    # Cây ngoại lệ chuyên biệt
├── logger.py                        # Logger chuẩn hóa
├── main.py                          # Điểm chạy chương trình chính
├── test_oop.py                      # Bộ Unit Test kiểm thử OOP và Ngoại lệ
├── du_an.json                       # Dữ liệu các dự án và công việc
├── du_lieu_moc.json                 # Dữ liệu tài khoản thành viên hệ thống
├── nhat_ky.json                     # Nhật ký lịch sử chuyển trạng thái
│
├── models/                          # Tầng Mô hình dữ liệu (Models)
│   ├── __init__.py                  # Export toàn bộ models
│   ├── DuAn.py                      # Model Dự án
│   ├── BinhLuan.py                  # Model Bình luận trên thẻ công việc
│   ├── ThanhVien.py                 # Proxy tương thích ngược trỏ về NguoiDung
│   │
│   ├── CongViec/                    # Package Công việc
│   │   ├── __init__.py
│   │   ├── CongViecBase.py          # Abstract Base Class CongViec(ABC)
│   │   ├── CongViecThuong.py        # Class CongViecThuong
│   │   └── CongViecKhan.py          # Class CongViecKhan
│   │
│   └── NguoiDung/                   # Package Người dùng
│       ├── __init__.py
│       ├── NguoiDungBase.py         # Abstract Base Class NguoiDung(ABC)
│       ├── ThanhVien.py             # Class ThanhVien
│       └── QuanTriVien.py           # Class QuanTriVien
│
└── services/                        # Tầng Nghiệp vụ (Services)
    ├── __init__.py
    ├── QuanLyKaban.py               # Facade Controller điều phối chính
    ├── XacThucService.py            # Dịch vụ đăng nhập & phiên người dùng
    ├── DuAnService.py               # Dịch vụ CRUD dự án & thành viên dự án
    ├── CongViecService.py           # Dịch vụ CRUD công việc, chuyển cột, bình luận, lọc
    │
    └── BoLuuTru/                    # Package Lưu trữ dữ liệu
        ├── __init__.py
        ├── BoLuuTruBase.py          # Abstract Base Class BoLuuTruBase(ABC)
        └── BoLuuTruMock.py          # Cài đặt đọc/ghi file JSON
```

---

## 🚀 4. Hướng Dẫn Chạy Chương Trình

### 4.1. Chạy Ứng Dụng Chính
```powershell
python main.py
```
*Kết quả:* Hệ thống tự động xác thực tài khoản quản trị, nạp dữ liệu từ `du_an.json` và hiển thị danh sách các dự án cùng các công việc theo từng trạng thái.

### 4.2. Chạy Kiểm Thử Tự Động (Unit Test)
```powershell
python test_oop.py
```
*Bộ test kiểm tra toàn diện 10 ca kiểm thử:*
1. Không thể khởi tạo Abstract Class (`CongViec`, `NguoiDung`, `BoLuuTruBase`).
2. Kiểm tra quan hệ kế thừa giữa các lớp con và lớp cha.
3. Kiểm tra tính đóng gói và validation gán giá trị hợp lệ.
4. Đa hình cảnh báo công việc (`canh_bao()`).
5. Đa hình phân quyền người dùng (`QuanTriVien` vs `ThanhVien`).
6. Bắt ngoại lệ xác thực đăng nhập (`XacThucThatBaiError`, `KhongTimThayError`).
7. Bắt ngoại lệ xung đột trùng lặp (`XungDotDuLieuError`).
8. Bắt ngoại lệ không có quyền truy cập (`KhongCoQuyenError`).
9. Kiểm tra tính toàn vẹn dữ liệu và cơ chế Transaction Rollback khi tầng lưu trữ gặp sự cố.
10. Kiểm tra thêm, xóa và đóng gói Bình luận (`BinhLuan`) trên thẻ công việc.



---

## 👥 5. Danh Sách Tài Khoản Mẫu Trong Hệ Thống (`du_lieu_moc.json`)

| Tên đăng nhập | Mật khẩu | Họ và tên | Vai trò | Quyền hạn |
| :--- | :---: | :--- | :---: | :--- |
| `admin` | `123456` | Quản trị viên Hệ thống | `quan_tri` | Toàn quyền trên mọi dự án và công việc |
| `quoc` | `123456` | Trịnh Quốc | `thanh_vien` | Thao tác dự án tham gia & công việc được giao |
| `khoa` | `123456` | Đăng Khoa | `thanh_vien` | Thao tác dự án tham gia & công việc được giao |
| `huy` | `123456` | Gia Huy | `thanh_vien` | Thao tác dự án tham gia & công việc được giao |
| `phu` | `123456` | Hồng Phú | `thanh_vien` | Thao tác dự án tham gia & công việc được giao |
