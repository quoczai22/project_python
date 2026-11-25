"""TaoDuAnDialog: Hộp thoại tạo dự án mới dành cho Quản trị viên."""
import re
import tkinter as tk
from tkinter import messagebox
import customtkinter as ctk

from logger import logger
from config import TRANG_THAI_HOP_LE
from exceptions import (
    KanbanException, DuLieuKhongHopLeError, KhongCoQuyenError,
    XungDotDuLieuError, LoiLuuTruError
)
from ui.styles import theme
from utils.helpers import can_giua


class TaoDuAnDialog(tk.Toplevel):
    """Tạo dự án mới (Dành cho Quản trị viên)."""

    def __init__(self, master, ql, khi_xong=None):
        super().__init__(master)
        self.ql = ql
        self.khi_xong = khi_xong

        self.title("Tạo dự án mới")
        self.configure(bg=theme.MAU_THE)
        self.resizable(False, False)
        self.transient(master)

        khung_ngoai = tk.Frame(self, bg=theme.MAU_THE)
        khung_ngoai.pack(fill="both", expand=True)

        theme.tao_header_figma(
            khung_ngoai, tieu_de="Khởi tạo dự án mới", badge_text="DA", cao=82
        )

        khung = tk.Frame(khung_ngoai, bg=theme.MAU_THE, padx=26, pady=18)
        khung.pack(fill="both", expand=True)

        tk.Label(
            khung, text="Mã dự án (Hệ thống tự cấp tăng tiến)", bg=theme.MAU_THE,
            fg=theme.MAU_CHU_NHAN, font=theme.FONT_DAM, anchor="w"
        ).pack(fill="x", pady=(0, 4))
        self.ma_du_an_sinh = self._sinh_ma()
        self.khung_ma = tk.Frame(
            khung, bg="#f8fafc", highlightthickness=1,
            highlightbackground="#cbd5e1", height=38
        )
        self.khung_ma.pack(fill="x", pady=(0, 10))
        self.khung_ma.pack_propagate(False)

        self.lbl_ma_da = tk.Label(
            self.khung_ma, text=self.ma_du_an_sinh, bg="#f8fafc", fg="#4338ca",
            font=theme.FONT_DAM, padx=12
        )
        self.lbl_ma_da.pack(side="left", fill="y")

        tk.Label(
            self.khung_ma, text="(Tự động cấp tăng tiến)", bg="#f8fafc", fg="#64748b",
            font=theme.FONT_NHO, padx=10
        ).pack(side="right", fill="y")

        tk.Label(
            khung, text="Tên dự án * (3-100 ký tự)", bg=theme.MAU_THE,
            fg=theme.MAU_CHU_NHAN, font=theme.FONT_DAM, anchor="w"
        ).pack(fill="x", pady=(0, 4))
        self.ent_ten = theme.tao_entry(khung, placeholder="Nhập tên dự án...", cao=38)
        self.ent_ten.pack(fill="x", pady=(0, 8))

        self.lbl_loi = tk.Label(
            khung, text="", bg=theme.MAU_THE, fg="#dc2626",
            font=theme.FONT_NHO, anchor="w"
        )
        self.lbl_loi.pack(fill="x", pady=(0, 8))

        tk.Label(
            khung, text="Quy trình cột Kanban mặc định", bg=theme.MAU_THE,
            fg=theme.MAU_CHU_NHAN, font=theme.FONT_DAM, anchor="w"
        ).pack(fill="x", pady=(0, 4))
        khung_cot = ctk.CTkFrame(khung, fg_color=theme.MAU_CHINH_NHAT, corner_radius=0)
        khung_cot.pack(fill="x", pady=(0, 16))
        tk.Label(
            khung_cot, text="   →   ".join(TRANG_THAI_HOP_LE),
            bg=theme.MAU_CHINH_NHAT, fg=theme.MAU_CHINH_DAM,
            font=theme.FONT_DAM, pady=9
        ).pack()

        tk.Frame(khung, bg="#edf1f4", height=1).pack(fill="x", pady=(2, 12))
        hang_nut = tk.Frame(khung, bg=theme.MAU_THE)
        hang_nut.pack(fill="x")

        theme.tao_nut_chinh(
            hang_nut, text="Tạo dự án", command=self.luu, width=128, height=38
        ).pack(side="right")

        theme.tao_nut_phu(
            hang_nut, text="Hủy", command=self.destroy, width=96, height=38
        ).pack(side="right", padx=(0, 8))

        self.ent_ten.bind("<Return>", lambda _e: self.luu())
        self.bind("<Escape>", lambda _e: self.destroy())
        can_giua(self, 520, 460)
        self.ent_ten.focus_set()
        self.wait_visibility()
        self.grab_set()

    def _sinh_ma(self):
        so = []
        try:
            for d in self.ql.lay_danh_sach_du_an():
                m = re.fullmatch(r"DA-(\d+)", d.ma_du_an)
                if m:
                    so.append(int(m.group(1)))
        except KanbanException as loi:
            logger.warning(f"Không đọc được danh sách dự án để sinh mã: {loi.thong_diep}")
        return f"DA-{(max(so) + 1 if so else 1):03d}"

    def _dat_loi(self, msg: str):
        self.lbl_loi.configure(text=msg)

    def luu(self):
        self._dat_loi("")
        ma = self.ma_du_an_sinh
        ten = self.ent_ten.get().strip()

        if not ten:
            self._dat_loi("Tên dự án không được để trống.")
            self.ent_ten.focus_set()
            return
        if len(ten) < 3 or len(ten) > 100:
            self._dat_loi("Tên dự án phải từ 3 đến 100 ký tự.")
            self.ent_ten.focus_set()
            return

        try:
            du_an = self.ql.tao_du_an(ma, ten)
        except DuLieuKhongHopLeError as loi:
            self._dat_loi(loi.thong_diep)
            return
        except XungDotDuLieuError as loi:
            self._dat_loi(loi.thong_diep)
            messagebox.showerror("Trùng lặp", loi.thong_diep, parent=self)
            return
        except KhongCoQuyenError as loi:
            messagebox.showerror("Từ chối quyền", loi.thong_diep, parent=self)
            return
        except LoiLuuTruError as loi:
            messagebox.showerror("Lỗi lưu trữ", loi.thong_diep, parent=self)
            return
        except KanbanException as loi:
            self._dat_loi(loi.thong_diep)
            return
        except Exception as e:
            messagebox.showerror("Lỗi hệ thống", f"Không thể tạo dự án: {e}", parent=self)
            return

        self.destroy()
        if self.khi_xong:
            self.khi_xong(du_an)
