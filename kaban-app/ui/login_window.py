"""Cửa sổ đăng nhập và tạo tài khoản theo thiết kế Figma (Tkinter + CustomTkinter)."""
import re
import tkinter as tk
from tkinter import messagebox
import customtkinter as ctk

from config import MAT_KHAU_TOI_THIEU, MAU_TEN_DANG_NHAP, MAU_EMAIL
from exceptions import (
    KanbanException, DuLieuKhongHopLeError, XacThucThatBaiError,
    XungDotDuLieuError, LoiLuuTruError
)
from ui.styles import theme
from utils.helpers import can_giua


class LoginWindow(tk.Toplevel):
    """Cửa sổ đăng nhập. Đăng nhập xong sẽ gọi khi_dang_nhap_thanh_cong(nguoi_dung)."""

    def __init__(self, master, ql, khi_dang_nhap_thanh_cong):
        super().__init__(master)
        self.ql = ql
        self.khi_dang_nhap_thanh_cong = khi_dang_nhap_thanh_cong

        self.title("Kanban Workspace - Đăng nhập")
        self.configure(bg=theme.MAU_NEN)
        self.resizable(False, False)
        self.protocol("WM_DELETE_WINDOW", self._thoat)

        self.var_hien_mk = tk.BooleanVar(value=False)
        self.var_hien_mk_dk = tk.BooleanVar(value=False)

        self._dung_giao_dien()
        can_giua(self, 510, 710)
        self.lift()
        self.attributes("-topmost", True)
        self.after_idle(self.attributes, "-topmost", False)
        self.ent_dn_ten.focus_set()

    # ---------------------------------------------------------------- giao diện
    def _dung_giao_dien(self):
        khung_ngoai = ctk.CTkFrame(
            self, fg_color=theme.MAU_THE, corner_radius=0,
            border_width=1, border_color=theme.MAU_VIEN_THE
        )
        khung_ngoai.pack(fill="both", expand=True, padx=10, pady=10)

        header_boc = tk.Frame(khung_ngoai, bg=theme.MAU_THE)
        header_boc.pack(fill="x", padx=6, pady=(6, 0))
        theme.tao_header_figma(
            header_boc,
            tieu_de="Đăng nhập hệ thống Kanban",
            cao=82
        )

        # Thanh chuyển tab dạng pill trắng trên nền xám nhạt để đảm bảo độ tương phản
        seg_frame = tk.Frame(khung_ngoai, bg=theme.MAU_THE)
        seg_frame.pack(fill="x", padx=28, pady=(16, 4))

        self.seg_che_do = ctk.CTkSegmentedButton(
            seg_frame,
            values=["Đăng nhập", "Tạo tài khoản"],
            command=self._chuyen_tab,
            font=theme.FONT_DAM,
            fg_color=theme.MAU_COT,
            selected_color=theme.MAU_THE,
            selected_hover_color=theme.MAU_THE,
            unselected_color=theme.MAU_COT,
            unselected_hover_color="#d5dfe7",
            text_color=theme.MAU_CHU,
            border_width=3,
            height=38,
            corner_radius=0
        )
        self.seg_che_do.pack(fill="x")
        self.seg_che_do.set("Đăng nhập")

        self.vung_noi_dung = tk.Frame(khung_ngoai, bg=theme.MAU_THE)
        self.vung_noi_dung.pack(fill="both", expand=True, padx=28, pady=(8, 18))

        self.tab_dang_nhap = tk.Frame(self.vung_noi_dung, bg=theme.MAU_THE)
        self.tab_tao_tk = tk.Frame(self.vung_noi_dung, bg=theme.MAU_THE)

        self._dung_tab_dang_nhap(self.tab_dang_nhap)
        self._dung_tab_tao_tai_khoan(self.tab_tao_tk)

        self.tab_dang_nhap.pack(fill="both", expand=True)

    def _chuyen_tab(self, ten_tab):
        if hasattr(self, "lbl_thong_bao"):
            self.lbl_thong_bao.configure(text="")
        if ten_tab == "Đăng nhập":
            self.tab_tao_tk.pack_forget()
            self.tab_dang_nhap.pack(fill="both", expand=True)
            self.ent_dn_ten.focus_set()
        else:
            self.tab_dang_nhap.pack_forget()
            self.tab_tao_tk.pack(fill="both", expand=True)
            self.ent_dk_ten.focus_set()

    def _them_o_nhap(self, cha, nhan: str, placeholder: str = "",
                     an_chu: bool = False, cao: int = 38, khoang_cach: int = 10):
        """Tạo cặp Label + CTkEntry bo góc có placeholder và viền focus."""
        tk.Label(
            cha, text=nhan, bg=theme.MAU_THE, fg=theme.MAU_CHU_NHAN,
            font=theme.FONT_DAM, anchor="w"
        ).pack(fill="x", pady=(khoang_cach, 4))

        o_nhap = theme.tao_entry(
            cha, placeholder=placeholder, an_chu=an_chu, cao=cao
        )
        o_nhap.pack(fill="x")
        return o_nhap

    def _dung_tab_dang_nhap(self, cha):
        tk.Label(
            cha, text="Chào mừng trở lại", bg=theme.MAU_THE, fg=theme.MAU_CHU,
            font=theme.FONT_CHAO_MUNG, anchor="w"
        ).pack(fill="x", pady=(8, 2))
        tk.Label(
            cha, text="Đăng nhập để tiếp tục quản lý công việc.",
            bg=theme.MAU_THE, fg=theme.MAU_CHU_PHU, font=theme.FONT_NHO, anchor="w"
        ).pack(fill="x", pady=(0, 8))

        self.ent_dn_ten = self._them_o_nhap(
            cha, "Tên đăng nhập",
            placeholder="Nhập tên đăng nhập (VD: admin, quoc)", cao=42
        )
        self.ent_dn_mk = self._them_o_nhap(
            cha, "Mật khẩu",
            placeholder="Nhập mật khẩu", an_chu=True, cao=42
        )

        ctk.CTkCheckBox(
            cha, text="Hiện mật khẩu", variable=self.var_hien_mk,
            command=self._doi_hien_mat_khau,
            font=theme.FONT_NHO, text_color=theme.MAU_CHU_NHAN,
            fg_color=theme.MAU_CHINH, hover_color=theme.MAU_CHINH_DAM,
            border_color=theme.MAU_VIEN_THE, corner_radius=0,
            checkbox_width=18, checkbox_height=18
        ).pack(anchor="w", pady=(10, 0))

        theme.tao_nut_chinh(
            cha, text="Đăng nhập  →", command=self._xu_ly_dang_nhap,
            height=42
        ).pack(fill="x", pady=(14, 0))

        self.lbl_thong_bao = tk.Label(
            cha, text="", bg=theme.MAU_THE, fg=theme.MAU_LOI,
            font=theme.FONT_NHO, anchor="w"
        )
        self.lbl_thong_bao.pack(fill="x", pady=(6, 0))

        # Khu vực điền nhanh tài khoản mẫu để kiểm thử thuận tiện
        khung_mau = ctk.CTkFrame(
            cha, fg_color=theme.MAU_O_NHAP, corner_radius=0,
            border_width=1, border_color=theme.MAU_VIEN
        )
        khung_mau.pack(fill="x", pady=(12, 0))

        tk.Label(
            khung_mau,
            text="Chọn nhanh tài khoản mẫu (mật khẩu: 123456):",
            bg=theme.MAU_O_NHAP, fg=theme.MAU_CHU_PHU, font=theme.FONT_NHO, anchor="w"
        ).pack(fill="x", padx=12, pady=(8, 6))

        hang_chip = tk.Frame(khung_mau, bg=theme.MAU_O_NHAP)
        hang_chip.pack(fill="x", padx=12, pady=(0, 10))

        for ten_tk, nhan in (("admin", "admin (QT)"), ("quoc", "quoc"),
                             ("huy", "huy"), ("khoa", "khoa"), ("phu", "phu")):
            ctk.CTkButton(
                hang_chip, text=nhan,
                command=lambda t=ten_tk: self._dien_nhanh(t),
                width=86 if ten_tk == "admin" else 56, height=28, corner_radius=0,
                fg_color=theme.MAU_THE, hover_color=theme.MAU_CHINH_NHAT,
                border_width=1, border_color=theme.MAU_VIEN_THE,
                text_color=theme.MAU_CHINH_DAM, font=theme.FONT_NHO_DAM
            ).pack(side="left", padx=(0, 6))

        self.ent_dn_ten.bind("<Return>", lambda e: self.ent_dn_mk.focus_set())
        self.ent_dn_mk.bind("<Return>", lambda e: self._xu_ly_dang_nhap())

    def _dung_tab_tao_tai_khoan(self, cha):
        tk.Label(
            cha, text="Đăng ký thành viên mới", bg=theme.MAU_THE, fg=theme.MAU_CHU,
            font=theme.FONT_PHU_DE, anchor="w"
        ).pack(fill="x", pady=(4, 2))
        tk.Label(
            cha, text="Tài khoản đăng ký mới có vai trò Thành viên.",
            bg=theme.MAU_THE, fg=theme.MAU_CHU_PHU, font=theme.FONT_NHO, anchor="w"
        ).pack(fill="x", pady=(0, 2))

        self.ent_dk_ten = self._them_o_nhap(
            cha, "Tên đăng nhập * (3-20 ký tự không dấu, số hoặc _)",
            placeholder="VD: minh_anh01", cao=34, khoang_cach=4
        )
        self.ent_dk_ho_ten = self._them_o_nhap(
            cha, "Họ và tên", placeholder="VD: Nguyễn Văn An",
            cao=34, khoang_cach=4
        )
        self.ent_dk_email = self._them_o_nhap(
            cha, "Email (tùy chọn)", placeholder="VD: an@kanban.vn",
            cao=34, khoang_cach=4
        )
        self.ent_dk_mk = self._them_o_nhap(
            cha, f"Mật khẩu * (tối thiểu {MAT_KHAU_TOI_THIEU} ký tự)",
            placeholder="Nhập mật khẩu", an_chu=True, cao=34, khoang_cach=4
        )
        self.ent_dk_mk2 = self._them_o_nhap(
            cha, "Nhập lại mật khẩu *",
            placeholder="Nhập lại mật khẩu", an_chu=True, cao=34, khoang_cach=4
        )

        ctk.CTkCheckBox(
            cha, text="Hiện mật khẩu", variable=self.var_hien_mk_dk,
            command=self._doi_hien_mat_khau_dk,
            font=theme.FONT_NHO, text_color=theme.MAU_CHU_NHAN,
            fg_color=theme.MAU_CHINH, hover_color=theme.MAU_CHINH_DAM,
            border_color=theme.MAU_VIEN_THE, corner_radius=0,
            checkbox_width=18, checkbox_height=18
        ).pack(anchor="w", pady=(8, 0))

        theme.tao_nut_chinh(
            cha, text="Tạo tài khoản  →", command=self._xu_ly_tao_tai_khoan,
            height=40
        ).pack(fill="x", pady=(10, 0))

        self.ent_dk_mk2.bind("<Return>", lambda e: self._xu_ly_tao_tai_khoan())

    # ---------------------------------------------------------------- xử lý sự kiện
    def _dien_nhanh(self, ten_dang_nhap: str):
        theme.dat_gia_tri_entry(self.ent_dn_ten, ten_dang_nhap)
        theme.dat_gia_tri_entry(self.ent_dn_mk, "123456")
        if hasattr(self, "lbl_thong_bao"):
            self.lbl_thong_bao.configure(
                text=f"Đã điền mẫu tài khoản '{ten_dang_nhap}'.",
                fg=theme.MAU_CHINH_DAM
            )
        self.ent_dn_mk.focus_set()

    def _doi_hien_mat_khau(self):
        self.ent_dn_mk.configure(show="" if self.var_hien_mk.get() else "•")

    def _doi_hien_mat_khau_dk(self):
        ky_tu = "" if self.var_hien_mk_dk.get() else "•"
        self.ent_dk_mk.configure(show=ky_tu)
        self.ent_dk_mk2.configure(show=ky_tu)

    def _xu_ly_dang_nhap(self):
        ten = self.ent_dn_ten.get().strip()
        mat_khau = self.ent_dn_mk.get()
        if not ten:
            self._bao_loi("Vui lòng nhập tên đăng nhập.")
            self.ent_dn_ten.focus_set()
            return
        if not mat_khau:
            self._bao_loi("Vui lòng nhập mật khẩu.")
            self.ent_dn_mk.focus_set()
            return
        try:
            nguoi_dung = self.ql.dang_nhap(ten, mat_khau)
        except XacThucThatBaiError as loi:
            self._bao_loi(f"Đăng nhập thất bại: {loi.thong_diep}", popup=True)
            theme.dat_gia_tri_entry(self.ent_dn_mk, "")
            self.ent_dn_mk.focus_set()
            return
        except LoiLuuTruError as loi:
            self._bao_loi(f"Lỗi cơ sở dữ liệu: {loi.thong_diep}", popup=True)
            return
        except KanbanException as loi:
            self._bao_loi(loi.thong_diep, popup=True)
            return
        except Exception as loi:
            self._bao_loi(f"Lỗi hệ thống: {loi}", popup=True)
            return

        self.destroy()
        self.khi_dang_nhap_thanh_cong(nguoi_dung)

    def _xu_ly_tao_tai_khoan(self):
        ten = self.ent_dk_ten.get().strip()
        ho_ten = self.ent_dk_ho_ten.get().strip()
        email = self.ent_dk_email.get().strip()
        mat_khau = self.ent_dk_mk.get()
        mat_khau_2 = self.ent_dk_mk2.get()

        # 1. Validate tên đăng nhập
        if not ten:
            self._bao_loi("Tên đăng nhập không được để trống.", popup=True)
            self.ent_dk_ten.focus_set()
            return
        if not re.fullmatch(MAU_TEN_DANG_NHAP, ten):
            self._bao_loi(
                "Tên đăng nhập phải từ 3-20 ký tự, chỉ gồm chữ cái, số và dấu gạch dưới.",
                popup=True
            )
            self.ent_dk_ten.focus_set()
            return

        # 2. Validate họ và tên
        if not ho_ten:
            self._bao_loi("Họ và tên không được để trống.", popup=True)
            self.ent_dk_ho_ten.focus_set()
            return
        if len(ho_ten) < 2 or len(ho_ten) > 50:
            self._bao_loi("Họ và tên phải từ 2 đến 50 ký tự.", popup=True)
            self.ent_dk_ho_ten.focus_set()
            return

        # 3. Validate email
        if not email:
            self._bao_loi("Email không được để trống.", popup=True)
            self.ent_dk_email.focus_set()
            return
        if not re.fullmatch(MAU_EMAIL, email):
            self._bao_loi("Địa chỉ email không đúng định dạng (VD: ten@domain.com).", popup=True)
            self.ent_dk_email.focus_set()
            return

        # 4. Validate mật khẩu
        if not mat_khau:
            self._bao_loi("Mật khẩu không được để trống.", popup=True)
            self.ent_dk_mk.focus_set()
            return
        if len(mat_khau) < MAT_KHAU_TOI_THIEU:
            self._bao_loi(f"Mật khẩu phải có ít nhất {MAT_KHAU_TOI_THIEU} ký tự.", popup=True)
            self.ent_dk_mk.focus_set()
            return
        if mat_khau != mat_khau_2:
            self._bao_loi("Mật khẩu xác nhận không trùng khớp.", popup=True)
            self.ent_dk_mk2.focus_set()
            return

        # 5. Gọi nghiệp vụ và bắt ngoại lệ
        try:
            self.ql.dang_ky(ten, mat_khau, ho_ten, email)
        except XungDotDuLieuError as loi:
            self._bao_loi(f"Trùng lặp: {loi.thong_diep}", popup=True)
            return
        except DuLieuKhongHopLeError as loi:
            self._bao_loi(f"Dữ liệu không hợp lệ: {loi.thong_diep}", popup=True)
            return
        except LoiLuuTruError as loi:
            self._bao_loi(f"Lỗi lưu trữ: {loi.thong_diep}", popup=True)
            return
        except KanbanException as loi:
            self._bao_loi(loi.thong_diep, popup=True)
            return
        except Exception as loi:
            self._bao_loi(f"Lỗi hệ thống: {loi}", popup=True)
            return

        messagebox.showinfo(
            "Đăng ký thành công",
            f"Tài khoản '{ten}' đã được tạo thành công! Hãy đăng nhập để bắt đầu.",
            parent=self
        )
        theme.dat_gia_tri_entry(self.ent_dn_ten, ten)
        theme.dat_gia_tri_entry(self.ent_dn_mk, "")
        for ent in (self.ent_dk_ten, self.ent_dk_ho_ten, self.ent_dk_email,
                    self.ent_dk_mk, self.ent_dk_mk2):
            theme.dat_gia_tri_entry(ent, "")
        self.seg_che_do.set("Đăng nhập")
        self._chuyen_tab("Đăng nhập")
        self.ent_dn_mk.focus_set()

    def _bao_loi(self, thong_diep: str, popup: bool = False):
        """Hiển thị thông điệp lỗi trên nhãn trạng thái và/hoặc popup."""
        if hasattr(self, "lbl_thong_bao") and self.lbl_thong_bao.winfo_exists():
            self.lbl_thong_bao.configure(text=thong_diep, fg=theme.MAU_LOI)
        if popup:
            messagebox.showwarning("Cảnh báo", thong_diep, parent=self)

    def _thoat(self):
        """Đóng cửa sổ đăng nhập = thoát luôn ứng dụng."""
        if messagebox.askokcancel("Thoát", "Bạn có chắc muốn thoát ứng dụng?", parent=self):
            self.master.destroy()
