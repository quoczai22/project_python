from config import TEN_FILE_DU_AN, TEN_FILE_DU_LIEU_MOC
from services.QuanLyKaban import QuanLyKanban

if __name__ == "__main__":
    ql = QuanLyKanban(TEN_FILE_DU_AN, TEN_FILE_DU_LIEU_MOC)
    ql.dang_nhap("admin", "123456")

    danh_sach_du_an = ql.lay_danh_sach_du_an()

    if danh_sach_du_an:
        print("Danh sách dự án:")
        for du_an in danh_sach_du_an:
            print(f"  Mã dự án: {du_an.ma_du_an}")
            print(f"  Tên dự án: {du_an.ten_du_an}")
            print(f"  Danh sách công việc:")
            for cong_viec in du_an.cong_viec:
                print(f"    - {cong_viec.tieu_de} ({cong_viec.trang_thai})")
            print()
    else:
        print("Không có dự án nào.")
