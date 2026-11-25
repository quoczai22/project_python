# BÁO CÁO PHẦN VIỆC – PHÚ

## 1. Phạm vi thực hiện

Phú phụ trách mô-đun thống kê, tích hợp API/Crawl, kiểm thử tự động cho `QuanLyKanban`, JSON và thống kê; phối hợp tích hợp dữ liệu thống kê vào giao diện và lập bảng kết quả kiểm thử.

## 2. Thống kê tiến độ

Mô-đun `services/thong_ke.py` tổng hợp:

- Tổng số công việc.
- Số lượng và tỷ lệ hoàn thành.
- Số lượng và tỷ lệ chưa hoàn thành.
- Số công việc quá hạn (không tính công việc đã hoàn thành).
- Số công việc có ngày kết thúc thiếu hoặc sai định dạng.
- Phân bổ theo trạng thái và theo thành viên phụ trách.

Dữ liệu ngày không hợp lệ được ghi nhận riêng, tránh làm hỏng toàn bộ màn hình thống kê. Chức năng xuất báo cáo TXT/CSV có thêm số lượng chưa hoàn thành và ngày hạn không hợp lệ. `ui/views/stats_view.py` sử dụng hàm thống kê dùng chung để giảm trùng lặp xử lý.

## 3. API/Crawl và lưu JSON

Ứng dụng sử dụng DummyJSON Todos (`https://dummyjson.com/docs/todos`) làm nguồn dữ liệu mẫu. Luồng xử lý: chọn vị trí trang và số lượng → gọi API → làm sạch và lưu JSON → xem trước/chọn todo → chọn người phụ trách và mức ưu tiên → tạo thẻ ở cột “Cần làm”. Người dùng tiếp tục xử lý thẻ qua các cột Kanban hiện có. Trạng thái hoàn thành gốc được giữ trong mô tả để tham khảo, không bỏ qua quy trình xử lý. Todo đã nhập được nhận diện theo mã nguồn để tránh tạo trùng; hạn mặc định là 7 ngày. Các lỗi URL, HTTP, timeout, mất mạng và JSON không hợp lệ được xử lý để không làm dừng ứng dụng.

File dữ liệu API mặc định: `data/api_todos.json`. Khi nhập lại cùng dữ liệu, ứng dụng đánh dấu nguồn API trong mô tả để hạn chế tạo công việc trùng.

## 4. Kiểm thử

Đã bổ sung `tests/test_phu_nhiem_vu.py` với 22 test cho thống kê, xuất báo cáo, API/JSON và tích hợp facade. Toàn bộ dự án chạy bằng `python -m unittest discover tests` đạt **108/108 test thành công** (86 test hiện có + 22 test bổ sung).

Bảng đầu vào, kết quả mong đợi, kết quả thực tế và trạng thái được ghi tại `TESTCASES.md`.

## 5. Hướng dẫn chạy thử phần Phú

```bash
cd kaban-app
python -m unittest tests.test_phu_nhiem_vu -v
python -m unittest discover tests -v
python main.py
```

Sau khi mở ứng dụng, đăng nhập bằng tài khoản mẫu, mở một dự án và vào màn hình thống kê để xem KPI/biểu đồ; sử dụng chức năng xuất báo cáo để tạo file TXT hoặc CSV. Chức năng nhập công việc từ API sử dụng nút/luồng nhập API hiện có của ứng dụng.

## 6. Ghi chú phối hợp nhóm từ nội dung họp

Các ý sau được ghi nhận để nhóm thống nhất và kiểm thử liên module; không được xem là đã hoàn tất chỉ bằng các test phần Phú:

- Làm rõ khác biệt quyền Admin, Leader và thành viên; ai được thêm/xóa thành viên.
- Quy định quy trình duyệt công việc mới và người có quyền duyệt.
- Quy định xử lý thành viên không hoàn thành nhiệm vụ và cách thu hồi quyền truy cập.
- Khi chuyển kỳ/tháng, công việc quá hạn chưa hoàn thành cần tiếp tục nằm trong danh sách chưa hoàn thành, không tự biến mất.
- Khi xóa công việc, cần xác định chính sách lưu lịch sử/soft delete; backup JSON phải giữ được bản dữ liệu trước thao tác và không bị ghi đè mất bản sao lưu tốt.

Các nội dung trên thuộc nghiệp vụ phân quyền, vòng đời công việc và lưu trữ; cần Quốc/Khoa/Huy cùng chốt schema và quyền trước khi tích hợp.

## 7. Kết luận

Phần thống kê, API và kiểm thử tự động đã được bổ sung và chạy đạt. Trước buổi bảo vệ, nhóm nên chạy thử giao diện trên máy trình chiếu, kiểm tra API khi có Internet và xác nhận các quy tắc phân quyền/lưu lịch sử nêu ở mục 6.

