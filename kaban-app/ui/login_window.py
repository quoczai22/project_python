"""Cửa sổ đăng nhập và tạo tài khoản theo thiết kế Figma (Tkinter + CustomTkinter)."""
import tkinter as tk
from tkinter import messagebox
import customtkinter as ctk

from exceptions import KanbanException
from ui import theme
from ui.tien_ich import can_giua


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

        # Biến liên kết với các ô nhập (StringVar)
        self.var_dn_ten = tk.StringVar()
        self.var_dn_mk = tk.StringVar()
        self.var_hien_mk = tk.BooleanVar(value=False)

        self.var_dk_ten = tk.StringVar()
        self.var_dk_ho_ten = tk.StringVar()
        self.var_dk_email = tk.StringVar()
        self.var_dk_mk = tk.StringVar()
        self.var_dk_mk2 = tk.StringVar()

        self._dung_giao_dien()
        can_giua(self, 470, 560)
        self.ent_dn_ten.focus_set()

    # ---------------------------------------------------------------- giao diện
    def _dung_giao_dien(self):
        # Khung thẻ modal bo góc ở giữa cửa sổ
        khung_ngoai = ctk.CTkFrame(
            self, fg_color=theme.MAU_THE, corner_radius=14,
            border_width=1, border_color=theme.MAU_VIEN
        )
        khung_ngoai.pack(fill="both", expand=True, padx=14, pady=14)

        # Header chuẩn Figma: KANBAN WORKSPACE / ĐĂNG NHẬP HỆ THỐNG KANBAN
        theme.tao_header_figma(
            khung_ngoai,
            eyebrow="KANBAN WORKSPACE",
            tieu_de="ĐĂNG NHẬP HỆ THỐNG KANBAN",
            cao=92
        )

        # Thanh chuyển chế độ Đăng nhập / Tạo tài khoản
        self_seg_frame = tk.Frame(khung_ngoai, bg=theme.MAU_THE)
        self_seg_frame.pack(fill="x", padx=32, pady=(16, 4))

        self.seg_che_do = ctk.CTkSegmentedButton(
            self_seg_frame,
            values=["Đăng nhập", "Tạo tài khoản"],
            command=self._chuyen_tab,
            font=theme.FONT_DAM,
            fg_color=theme.MAU_NEN,
            selected_color=theme.MAU_CHINH,
            selected_hover_color=theme.MAU_CHINH_DAM,
            unselected_color=theme.MAU_NEN,
            unselected_hover_color=theme.MAU_VIEN,
            text_color=theme.MAU_CHU,
            height=34,
            corner_radius=8
        )
        self.seg_che_do.pack(fill="x")
        self.seg_che_do.set("Đăng nhập")

        # Vùng chứa nội dung của 2 tab
        self.vung_noi_dung = tk.Frame(khung_ngoai, bg=theme.MAU_THE)
        self.vung_noi_dung.pack(fill="both", expand=True, padx=32, pady=(8, 20))

        self.tab_dang_nhap = tk.Frame(self.vung_noi_dung, bg=theme.MAU_THE)
        self.tab_tao_tk = tk.Frame(self.vung_noi_dung, bg=theme.MAU_THE)

        self._dung_tab_dang_nhap(self.tab_dang_nhap)
        self._dung_tab_tao_tai_khoan(self.tab_tao_tk)

        self.tab_dang_nhap.pack(fill="both", expand=True)

    def _chuyen_tab(self, ten_tab):
        if ten_tab == "Đăng nhập":
            self.tab_tao_tk.pack_forget()
            self.tab_dang_nhap.pack(fill="both", expand=True)
            self.ent_dn_ten.focus_set()
        else:
            self.tab_dang_nhap.pack_forget()
            self.tab_tao_tk.pack(fill="both", expand=True)
            self.ent_dk_ten.focus_set()

    def _them_o_nhap(self, cha, nhan, bien, placeholder="", an_chu=False, cao=38, khoang_cach=10):
        """Tạo cặp Label + CTkEntry bo góc chuẩn thiết kế Figma."""
        tk.Label(
            cha, text=nhan, bg=theme.MAU_THE, fg=theme.MAU_CHU_NHAN,
            font=theme.FONT_DAM, anchor="w"
        ).pack(fill="x", pady=(khoang_cach, 4))

        o_nhap = ctk.CTkEntry(
            cha,
            textvariable=bien,
            placeholder_text=placeholder,
            show="•" if an_chu else "",
            height=cao,
            corner_radius=7,
            fg_color=theme.MAU_O_NHAP,
            border_color=theme.MAU_VIEN_THE,
            border_width=1,
            text_color=theme.MAU_CHU,
            font=theme.FONT_CHUAN
        )
        o_nhap.pack(fill="x")
        return o_nhap

    def _dung_tab_dang_nhap(self, cha):
        # Phần giới thiệu giống .login-intro trong Figma
        tk.Label(
            cha, text="Chào mừng trở lại", bg=theme.MAU_THE, fg=theme.MAU_CHU,
            font=("Segoe UI", 14, "bold"), anchor="w"
        ).pack(fill="x", pady=(6, 2))
        tk.Label(
            cha, text="Đăng nhập để tiếp tục quản lý công việc.",
            bg=theme.MAU_THE, fg=theme.MAU_CHU_PHU, font=theme.FONT_NHO, anchor="w"
        ).pack(fill="x", pady=(0, 8))

        self.ent_dn_ten = self._them_o_nhap(
            cha, "Tên đăng nhập", self.var_dn_ten,
            placeholder="Nhập tên đăng nhập (VD: admin, quoc)"
        )
        self.ent_dn_mk = self._them_o_nhap(
            cha, "Mật khẩu", self.var_dn_mk,
            placeholder="Nhập mật khẩu", an_chu=True
        )

        # Checkbox hiện mật khẩu bo góc hiện đại
        ctk.CTkCheckBox(
            cha, text="Hiện mật khẩu", variable=self.var_hien_mk,
            command=self._doi_hien_mat_khau,
            font=theme.FONT_NHO, text_color=theme.MAU_CHU_NHAN,
            fg_color=theme.MAU_CHINH, hover_color=theme.MAU_CHINH_DAM,
            border_color=theme.MAU_VIEN_THE, corner_radius=5,
            checkbox_width=18, checkbox_height=18
        ).pack(anchor="w", pady=(12, 0))

        # Nút Đăng nhập màu Teal có mũi tên giống Figma
        ctk.CTkButton(
            cha, text="Đăng nhập   →",
            command=self._xu_ly_dang_nhap,
            height=42, corner_radius=7,
            fg_color=theme.MAU_CHINH, hover_color=theme.MAU_CHINH_DAM,
            text_color="white", font=theme.FONT_DAM
        ).pack(fill="x", pady=(22, 0))

        tk.Label(
            cha, text="Tài khoản mẫu: admin / 123456  •  quoc / 123456",
            bg=theme.MAU_THE, fg=theme.MAU_CHU_PHU, font=theme.FONT_NHO
        ).pack(pady=(12, 0))

        # Nhấn Enter ở 2 ô nhập cũng đăng nhập được
        self.ent_dn_ten.bind("<Return>", lambda e: self.ent_dn_mk.focus_set())
        self.ent_dn_mk.bind("<Return>", lambda e: self._xu_ly_dang_nhap())

    def _dung_tab_tao_tai_khoan(self, cha):
        self.ent_dk_ten = self._them_o_nhap(cha, "Tên đăng nhập", self.var_dk_ten, cao=32, khoang_cach=5)
        self._them_o_nhap(cha, "Họ và tên", self.var_dk_ho_ten, cao=32, khoang_cach=5)
        self._them_o_nhap(cha, "Email", self.var_dk_email, cao=32, khoang_cach=5)
        self._them_o_nhap(cha, "Mật khẩu (tối thiểu 6 ký tự)", self.var_dk_mk, an_chu=True, cao=32, khoang_cach=5)
        ent_mk2 = self._them_o_nhap(cha, "Nhập lại mật khẩu", self.var_dk_mk2, an_chu=True, cao=32, khoang_cach=5)

        ctk.CTkButton(
            cha, text="Tạo tài khoản   →",
            command=self._xu_ly_tao_tai_khoan,
            height=38, corner_radius=7,
            fg_color=theme.MAU_CHINH, hover_color=theme.MAU_CHINH_DAM,
            text_color="white", font=theme.FONT_DAM
        ).pack(fill="x", pady=(14, 0))
        ent_mk2.bind("<Return>", lambda e: self._xu_ly_tao_tai_khoan())

    # ---------------------------------------------------------------- xử lý sự kiện
    def _doi_hien_mat_khau(self):
        self.ent_dn_mk.configure(show="" if self.var_hien_mk.get() else "•")

    def _xu_ly_dang_nhap(self):
        ten = self.var_dn_ten.get().strip()
        mat_khau = self.var_dn_mk.get()
        if not ten or not mat_khau:
            messagebox.showwarning("Thiếu thông tin",
                                   "Vui lòng nhập tên đăng nhập và mật khẩu.", parent=self)
            return
        try:
            nguoi_dung = self.ql.dang_nhap(ten, mat_khau)
        except KanbanException as loi:
            messagebox.showerror("Đăng nhập thất bại", loi.thong_diep, parent=self)
            self.var_dn_mk.set("")
            self.ent_dn_mk.focus_set()
            return
        self.destroy()
        self.khi_dang_nhap_thanh_cong(nguoi_dung)

    def _xu_ly_tao_tai_khoan(self):
        ten = self.var_dk_ten.get().strip()
        ho_ten = self.var_dk_ho_ten.get().strip()
        email = self.var_dk_email.get().strip()
        mat_khau = self.var_dk_mk.get()

        if not ten or not mat_khau:
            messagebox.showwarning("Thiếu thông tin",
                                   "Tên đăng nhập và mật khẩu không được để trống.", parent=self)
            return
        if len(mat_khau) < 6:
            messagebox.showwarning("Mật khẩu yếu",
                                   "Mật khẩu phải có ít nhất 6 ký tự.", parent=self)
            return
        if mat_khau != self.var_dk_mk2.get():
            messagebox.showwarning("Không khớp", "Hai lần nhập mật khẩu không giống nhau.", parent=self)
            return

        if not hasattr(self.ql, "dang_ky"):
            messagebox.showinfo(
                "Chưa hỗ trợ",
                "Backend chưa có hàm QuanLyKanban.dang_ky().\nHãy nhắn Khoa bổ sung rồi thử lại.",
                parent=self)
            return

        try:
            self.ql.dang_ky(ten, mat_khau, ho_ten, email)
        except KanbanException as loi:
            messagebox.showerror("Tạo tài khoản thất bại", loi.thong_diep, parent=self)
            return

        messagebox.showinfo("Thành công", f"Đã tạo tài khoản '{ten}'. Hãy đăng nhập.", parent=self)
        self.var_dn_ten.set(ten)
        self.var_dn_mk.set("")
        for bien in (self.var_dk_ten, self.var_dk_ho_ten, self.var_dk_email,
                     self.var_dk_mk, self.var_dk_mk2):
            bien.set("")
        self.seg_che_do.set("Đăng nhập")
        self._chuyen_tab("Đăng nhập")
        self.ent_dn_mk.focus_set()

    def _thoat(self):
        """Đóng cửa sổ đăng nhập = thoát luôn ứng dụng (có hỏi xác nhận)."""
        if messagebox.askokcancel("Thoát", "Bạn có chắc muốn thoát ứng dụng?", parent=self):
            self.master.destroy()
