from config import TEN_FILE_DU_AN, TEN_FILE_DU_LIEU_MOC
from services.QuanLyKaban import QuanLyKanban
from exceptions import KanbanException
from logger import logger


if __name__ == "__main__":
    try:
        # Khởi tạo dịch vụ quản lý Kanban
        ql = QuanLyKanban(TEN_FILE_DU_AN, TEN_FILE_DU_LIEU_MOC)

        # Đăng nhập vào hệ thống
        ql.dang_nhap("admin", "123456")

        # Lấy danh sách dự án
        danh_sach_du_an = ql.lay_danh_sach_du_an()

        if danh_sach_du_an:
            print("\nDanh sách dự án:")
            for du_an in danh_sach_du_an:
                print(f"  Mã dự án: {du_an.ma_du_an}")
                print(f"  Tên dự án: {du_an.ten_du_an}")
                print(f"  Danh sách công việc:")
                for cong_viec in du_an.cong_viec:
                    print(f"    - {cong_viec.tieu_de} ({cong_viec.trang_thai})")
                print()
        else:
            print("Không có dự án nào.")

    except KanbanException as e:
        logger.error(f"Lỗi: {e}")
    except Exception as e:
        logger.critical(f"Lỗi hệ thống: {e}")
