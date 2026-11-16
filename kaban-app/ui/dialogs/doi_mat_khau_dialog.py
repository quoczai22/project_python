"""DoiMatKhauDialog: Hộp thoại đổi mật khẩu người dùng hiện tại."""
import tkinter as tk
from tkinter import messagebox
import customtkinter as ctk

from config import MAT_KHAU_TOI_THIEU
from exceptions import (
    KanbanException, XacThucThatBaiError, DuLieuKhongHopLeError, LoiLuuTruError
)
from ui.styles import theme
from utils.helpers import can_giua


class DoiMatKhauDialog(tk.Toplevel):
    """Hộp thoại cho phép người dùng đổi mật khẩu (nhập mật khẩu cũ + mới + xác nhận)."""

    def __init__(self, master, ql, khi_xong=None):
        super().__init__(master)
        self.ql = ql
        self.khi_xong = khi_xong

        self.title("Đổi mật khẩu")
        self.configure(bg=theme.MAU_THE)
        self.resizable(False, False)
        self.transient(master)

        self.var_hien_mk = tk.BooleanVar(value=False)

        self._dung_giao_dien()
        can_giua(self, 460, 500)
        self.minsize(460, 500)
        self.ent_mk_cu.focus_set()
        self.bind("<Escape>", lambda _e: self.destroy())
        self.wait_visibility()
        self.grab_set()

    def _them_o_nhap(self, cha, nhan: str, placeholder: str = "", an_chu: bool = False):
        """Tạo cặp Label + CTkEntry cho form đổi mật khẩu."""
        tk.Label(
            cha, text=nhan, bg=theme.MAU_THE, fg=theme.MAU_CHU_NHAN,
            font=theme.FONT_DAM, anchor="w"
        ).pack(fill="x", pady=(10, 4))

        o_nhap = theme.tao_entry(
            cha, placeholder=placeholder, an_chu=an_chu, cao=38
        )
        o_nhap.pack(fill="x")
        return o_nhap

    def _dung_giao_dien(self):
        khung_ngoai = ctk.CTkFrame(
            self, fg_color=theme.MAU_THE, corner_radius=0,
            border_width=1, border_color=theme.MAU_VIEN_THE
        )
        khung_ngoai.pack(fill="both", expand=True, padx=10, pady=10)

        theme.tao_header_figma(
            khung_ngoai,
            tieu_de="Đổi mật khẩu tài khoản",
            badge_text="MK",
            cao=68
        )

        # Footer nút bấm đóng gói dưới đáy trước để luôn luôn hiển thị
        footer = tk.Frame(khung_ngoai, bg=theme.MAU_THE, padx=28, pady=12)
        footer.pack(side="bottom", fill="x")
        tk.Frame(footer, bg="#edf1f4", height=1).pack(fill="x", pady=(0, 10))

        hang_nut = tk.Frame(footer, bg=theme.MAU_THE)
        hang_nut.pack(fill="x")

        self.btn_xac_nhan = theme.tao_nut_chinh(
            hang_nut, text="Xác nhận", command=self._xu_ly_doi_mat_khau,
            width=130, height=38
        )
        self.btn_xac_nhan.pack(side="right")

        theme.tao_nut_phu(
            hang_nut, text="Hủy", command=self.destroy,
            width=80, height=38
        ).pack(side="right", padx=(0, 8))

        nd = self.ql.nguoi_dung_hien_tai
        ten_hien_thi = f"{nd.ho_ten} ({nd.ten_dang_nhap})" if nd else ""

        khung = tk.Frame(khung_ngoai, bg=theme.MAU_THE, padx=28, pady=8)
        khung.pack(side="top", fill="both", expand=True)

        tk.Label(
            khung, text=f"Tài khoản: {ten_hien_thi}",
            bg=theme.MAU_THE, fg=theme.MAU_CHU_PHU,
            font=theme.FONT_NHO, anchor="w"
        ).pack(fill="x", pady=(4, 0))

        self.ent_mk_cu = self._them_o_nhap(
            khung, "Mật khẩu hiện tại *",
            placeholder="Nhập mật khẩu hiện tại", an_chu=True
        )
        self.ent_mk_moi = self._them_o_nhap(
            khung, f"Mật khẩu mới * (tối thiểu {MAT_KHAU_TOI_THIEU} ký tự)",
            placeholder="Nhập mật khẩu mới", an_chu=True
        )
        self.ent_mk_xn = self._them_o_nhap(
            khung, "Nhập lại mật khẩu mới *",
            placeholder="Xác nhận mật khẩu mới", an_chu=True
        )

        ctk.CTkCheckBox(
            khung, text="Hiện mật khẩu", variable=self.var_hien_mk,
            command=self._doi_hien_mat_khau,
            font=theme.FONT_NHO, text_color=theme.MAU_CHU_NHAN,
            fg_color=theme.MAU_CHINH, hover_color=theme.MAU_CHINH_DAM,
            border_color=theme.MAU_VIEN_THE, corner_radius=0,
            checkbox_width=18, checkbox_height=18
        ).pack(anchor="w", pady=(10, 0))

        self.lbl_thong_bao = tk.Label(
            khung, text="", bg=theme.MAU_THE, fg=theme.MAU_LOI,
            font=theme.FONT_NHO, anchor="w", wraplength=360
        )
        self.lbl_thong_bao.pack(fill="x", pady=(8, 0))

        # Bind Enter
        self.ent_mk_cu.bind("<Return>", lambda _e: self.ent_mk_moi.focus_set())
        self.ent_mk_moi.bind("<Return>", lambda _e: self.ent_mk_xn.focus_set())
        self.ent_mk_xn.bind("<Return>", lambda _e: self._xu_ly_doi_mat_khau())

    def _doi_hien_mat_khau(self):
        ky_tu = "" if self.var_hien_mk.get() else "•"
        self.ent_mk_cu.configure(show=ky_tu)
        self.ent_mk_moi.configure(show=ky_tu)
        self.ent_mk_xn.configure(show=ky_tu)

    def _xu_ly_doi_mat_khau(self):
        mk_cu = self.ent_mk_cu.get()
        mk_moi = self.ent_mk_moi.get()
        mk_xn = self.ent_mk_xn.get()

        if not mk_cu:
            self._bao_loi("Vui lòng nhập mật khẩu hiện tại.")
            self.ent_mk_cu.focus_set()
            return
        if not mk_moi:
            self._bao_loi("Vui lòng nhập mật khẩu mới.")
            self.ent_mk_moi.focus_set()
            return
        if len(mk_moi) < MAT_KHAU_TOI_THIEU:
            self._bao_loi(f"Mật khẩu mới phải có ít nhất {MAT_KHAU_TOI_THIEU} ký tự.")
            self.ent_mk_moi.focus_set()
            return
        if mk_moi != mk_xn:
            self._bao_loi("Mật khẩu xác nhận không trùng khớp.")
            self.ent_mk_xn.focus_set()
            return
        if mk_moi == mk_cu:
            self._bao_loi("Mật khẩu mới phải khác mật khẩu hiện tại.")
            self.ent_mk_moi.focus_set()
            return

        try:
            self.ql.doi_mat_khau(mk_cu, mk_moi)
        except XacThucThatBaiError as loi:
            self._bao_loi(f"Sai mật khẩu: {loi.thong_diep}")
            theme.dat_gia_tri_entry(self.ent_mk_cu, "")
            self.ent_mk_cu.focus_set()
            return
        except DuLieuKhongHopLeError as loi:
            self._bao_loi(f"Không hợp lệ: {loi.thong_diep}")
            return
        except LoiLuuTruError as loi:
            self._bao_loi(f"Lỗi lưu trữ: {loi.thong_diep}")
            return
        except KanbanException as loi:
            self._bao_loi(loi.thong_diep)
            return
        except Exception as loi:
            self._bao_loi(f"Lỗi hệ thống: {loi}")
            return

        messagebox.showinfo(
            "Thành công",
            "Mật khẩu đã được đổi thành công!",
            parent=self
        )
        self.destroy()
        if self.khi_xong:
            self.khi_xong()

    def _bao_loi(self, thong_diep: str):
        self.lbl_thong_bao.configure(text=thong_diep, fg=theme.MAU_LOI)
        messagebox.showwarning("Cảnh báo", thong_diep, parent=self)
