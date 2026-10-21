"""File chạy thử giao diện của Huy (Quốc sẽ nối vào main.py sau)."""
import tkinter as tk

from config import TEN_FILE_DU_AN, TEN_FILE_DU_LIEU_MOC
from services.QuanLyKaban import QuanLyKanban
from ui import theme
from ui.login_window import LoginWindow
from ui.main_window import MainWindow


def main():
    ql = QuanLyKanban(TEN_FILE_DU_AN, TEN_FILE_DU_LIEU_MOC)

    goc = tk.Tk()
    goc.withdraw()
    theme.ap_dung_style()

    def mo_dang_nhap():
        LoginWindow(goc, ql, mo_cua_so_chinh)

    def mo_cua_so_chinh(nguoi_dung):
        MainWindow(goc, ql, khi_dang_xuat=mo_dang_nhap)

    mo_dang_nhap()
    goc.mainloop()


if __name__ == "__main__":
    main()