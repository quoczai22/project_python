"""main.py: Điểm khởi chạy duy nhất (Entry point) hợp nhất toàn bộ Backend và Frontend.

Cách chạy:
    - Chạy bình thường (giao diện đăng nhập):  python main.py
    - Chạy thẳng với quyền Admin:              python main.py --admin
    - Chạy chế độ Terminal/CLI:               python main.py --cli
"""
import sys
import tkinter as tk

from config import TEN_FILE_DU_AN, TEN_FILE_DU_LIEU_MOC
from services.QuanLyKaban import QuanLyKanban
from ui.styles import theme
from ui.login_window import LoginWindow
from ui.main_window import MainWindow
from logger import logger


def chay_che_do_cli(ql: QuanLyKanban):
    """Chạy chế độ console terminal để in nhanh danh sách dự án."""
    print("=" * 60)
    print("             ỨNG DỤNG QUẢN LÝ TIẾN ĐỘ KANBAN (CLI)")
    print("=" * 60)
    try:
        ql.dang_nhap("admin", "123456")
        ds = ql.lay_danh_sach_du_an()
        if not ds:
            print("Chưa có dự án nào trong hệ thống.")
            return
        for da in ds:
            print(f"\n[DỰ ÁN] {da.ma_du_an} — {da.ten_du_an} ({len(da.cong_viec)} công việc)")
            for cv in da.cong_viec:
                print(f"  • [{cv.ma_cong_viec}] {cv.tieu_de:<30} | {cv.trang_thai:<12} | Ưu tiên: {cv.muc_uu_tien}")
    except Exception as err:
        print(f"Lỗi CLI: {err}")
    print("=" * 60)


def chay_giao_dien(ql: QuanLyKanban):
    """Khởi chạy ứng dụng giao diện đồ họa (GUI) chuẩn Figma."""
    goc = tk.Tk()
    goc.withdraw()
    theme.ap_dung_style()

    def mo_dang_nhap():
        LoginWindow(goc, ql, mo_cua_so_chinh)

    def mo_cua_so_chinh(_nguoi_dung):
        MainWindow(goc, ql, khi_dang_xuat=mo_dang_nhap)

    # Nếu truyền cờ --admin hoặc --direct thì tự động đăng nhập admin
    if "--admin" in sys.argv or "--direct" in sys.argv:
        try:
            nd = ql.dang_nhap("admin", "123456")
            mo_cua_so_chinh(nd)
        except Exception as err:
            logger.warning(f"Không thể tự đăng nhập admin: {err}. Mở màn hình đăng nhập.")
            mo_dang_nhap()
    else:
        mo_dang_nhap()

    goc.mainloop()


def main():
    logger.info("Khởi động Ứng dụng Quản lý Kanban...")
    ql = QuanLyKanban(TEN_FILE_DU_AN, TEN_FILE_DU_LIEU_MOC)

    if "--cli" in sys.argv:
        chay_che_do_cli(ql)
    else:
        chay_giao_dien(ql)


if __name__ == "__main__":
    main()
