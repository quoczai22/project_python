# Bàn giao phần Khoa

## Chạy thử

Mở PowerShell tại `kaban-app`. Bản local có môi trường Python riêng trong `.venv`. Với bản mới tải về, tạo môi trường và cài thư viện trước khi chạy.

```powershell
python -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
.\.venv\Scripts\python.exe main.py
```

Đăng nhập bằng `admin` để xem đủ 6 dự án và 58 công việc. Đăng nhập bằng `khoa` để thử quyền thành viên trên các dự án DA-001, DA-003 và DA-005. Các tài khoản có sẵn dùng mật khẩu demo `123456`. Có thể thử thêm `demo_an` để xem quyền trên dự án thư viện và cổng học liệu.

Bộ dữ liệu thêm 4 dự án, 48 công việc, 6 tài khoản, 12 bình luận và 16 lượt chuyển trạng thái. Có đủ bốn cột Kanban, năm nhãn, việc thường và việc khẩn. Các hạn chót là ngày cố định quanh tháng 11/2026 để minh họa việc quá hạn và còn hạn tại thời điểm bàn giao. Số việc quá hạn thay đổi theo ngày chạy.

```powershell
.\.venv\Scripts\python.exe main.py --cli
.\.venv\Scripts\python.exe -m unittest discover tests
```

Chạy bộ kiểm thử trên một bản sao của thư mục ứng dụng vì một số ca thử dùng các đường dẫn dữ liệu mặc định.

## File và API

| File ứng dụng sử dụng | Cấu trúc |
| --- | --- |
| `data/du_an.json` | Danh sách dự án. Mỗi dự án có `MaDuAn`, `TenDuAn`, `DanhSachCot`, `ThanhVienThamGia`, `DanhSachCongViec` và `NgayTao`. Người phụ trách công việc dùng tên đăng nhập của thành viên trong dự án. |
| `data/du_lieu_moc.json` | Đối tượng có khóa `thanh_vien` chứa danh sách tài khoản. Mỗi tài khoản có tên đăng nhập, họ tên, email, vai trò và mật khẩu ở dạng `salt$sha256`. Tầng lưu trữ cũng đọc được danh sách tài khoản dạng cũ. |
| `data/nhat_ky.json` | Danh sách gồm người thao tác, thời gian, mã công việc, trạng thái cũ và mới. Các mục demo thêm `ma_du_an` để truy vết. |

- `BoLuuTruMock.doc_json(ten_file)` đọc JSON. Nếu file thiếu, rỗng, sai cú pháp hoặc sai kiểu gốc, hàm tìm bản sao lưu hợp lệ mới nhất. Lỗi lưu trữ dùng `LoiLuuTruError`.
- `ghi_json(ten_file, du_lieu)` sao lưu bản cũ rồi ghi file mới bằng thao tác thay thế nguyên tử. Khi sao lưu thất bại, hàm báo lỗi và giữ file gốc.
- `sao_luu(ten_file)` trả về đường dẫn bản sao lưu. `danh_sach_sao_luu(ten_file)` liệt kê từ bản mới đến bản cũ, tối đa 10 bản cho mỗi file. Bản hỏng được cất riêng với đuôi `.loi-<thời gian>`.
- `doc_danh_sach_thanh_vien()` trả về các đối tượng người dùng. `ghi_danh_sach_thanh_vien(danh_sach)` lưu tài khoản. Mật khẩu thô trong file tài khoản cũ được băm khi nâng cấp dữ liệu và khi tạo bản sao lưu JSON hợp lệ.
- `ghi_nhat_ky(ban_ghi)` thêm bản ghi, tự điền giờ nếu thiếu và trả về `True` hoặc `False`. `doc_nhat_ky()` lấy danh sách nhật ký.
- `QuanLyKanban.dang_ky(...)` tạo thành viên, `dang_nhap(...)` xác thực và trả về đối tượng người dùng, `dang_xuat()` xóa phiên, `doi_mat_khau(cu, moi)` đổi mật khẩu cho người đang đăng nhập. UI gọi các hàm này qua `QuanLyKanban`.

## Thử sao lưu và phục hồi trên bản sao

1. Sao chép thư mục ứng dụng để thử. Chạy lệnh bên dưới tại thư mục `kaban-app` của bản sao với Python đã cài thư viện.
2. Đổi tên `data/du_an.json` thành `du_an.kiem-tra`. Chạy `python main.py --cli` và kiểm tra ứng dụng đọc đủ 6 dự án, đồng thời tạo lại `du_an.json`.
3. Thử tiếp bằng một file `du_an.json` rỗng hoặc chứa `{}`. Lần đọc kế tiếp sẽ dùng backup và lưu riêng bản lỗi vào `data/backup/`. Có thể làm tương tự cho tài khoản và nhật ký trên bản sao.

```powershell
python -c "from services.BoLuuTru import BoLuuTruMock; b = BoLuuTruMock(); print(b.sao_luu(b.ten_file_du_an)); print(b.sao_luu(b.ten_file_du_lieu_moc)); print(b.sao_luu(b.ten_file_nhat_ky))"
```

Nếu cần tạo lại toàn bộ demo khi đã mất bản sao lưu, lấy ba file JSON từ bản bàn giao sạch. Khi mất file tài khoản và bản sao lưu, ứng dụng tự tạo hai tài khoản tối thiểu `admin` và `khoa`. Các bản sao tạo trong `data/backup/` chỉ nằm trên máy đang chạy.
