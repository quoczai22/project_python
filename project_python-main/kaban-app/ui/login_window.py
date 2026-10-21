"""Cửa sổ đăng nhập và tạo tài khoản."""
import tkinter as tk
from tkinter import ttk, messagebox

from exceptions import KanbanException
from ui import theme
from ui.tien_ich import can_giua


class LoginWindow(tk.Toplevel):
    """Cửa sổ đăng nhập. Đăng nhập xong sẽ gọi khi_dang_nhap_thanh_cong(nguoi_dung)."""

    def __init__(self, master, ql, khi_dang_nhap_thanh_cong):
        super().__init__(master)
        self.ql = ql
        self.khi_dang_nhap_thanh_cong = khi_dang_nhap_thanh_cong

        self.title("Kanban - Đăng nhập")
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
        can_giua(self, 400)
        self.ent_dn_ten.focus_set()

    # ---------------------------------------------------------------- giao diện
    def _dung_giao_dien(self):
        ttk.Label(self, text="KANBAN", font=theme.FONT_TIEU_DE,
                  foreground=theme.MAU_CHINH).pack(pady=(20, 0))
        ttk.Label(self, text="Quản lý công việc nhóm",
                  foreground=theme.MAU_CHU_PHU).pack(pady=(0, 10))

        self.tabs = ttk.Notebook(self)
        self.tabs.pack(fill="both", expand=True, padx=20, pady=(0, 20))

        tab_dang_nhap = ttk.Frame(self.tabs, padding=16)
        tab_tao_tk = ttk.Frame(self.tabs, padding=16)
        self.tabs.add(tab_dang_nhap, text="Đăng nhập")
        self.tabs.add(tab_tao_tk, text="Tạo tài khoản")

        self._dung_tab_dang_nhap(tab_dang_nhap)
        self._dung_tab_tao_tai_khoan(tab_tao_tk)

    def _them_o_nhap(self, cha, nhan, bien, an_chu=False):
        """Tạo cặp Label + Entry xếp dọc, trả về Entry."""
        ttk.Label(cha, text=nhan).pack(anchor="w", pady=(8, 2))
        o_nhap = ttk.Entry(cha, textvariable=bien, show="•" if an_chu else "")
        o_nhap.pack(fill="x")
        return o_nhap

    def _dung_tab_dang_nhap(self, cha):
        self.ent_dn_ten = self._them_o_nhap(cha, "Tên đăng nhập", self.var_dn_ten)
        self.ent_dn_mk = self._them_o_nhap(cha, "Mật khẩu", self.var_dn_mk, an_chu=True)

        # Checkbutton dùng command= để bật/tắt hiện mật khẩu
        ttk.Checkbutton(cha, text="Hiện mật khẩu", variable=self.var_hien_mk,
                        command=self._doi_hien_mat_khau).pack(anchor="w", pady=(8, 0))

        ttk.Button(cha, text="Đăng nhập", style="Chinh.TButton",
                   command=self._xu_ly_dang_nhap).pack(fill="x", pady=(18, 0))

        # bind: nhấn Enter ở 2 ô nhập cũng đăng nhập được
        self.ent_dn_ten.bind("<Return>", lambda e: self.ent_dn_mk.focus_set())
        self.ent_dn_mk.bind("<Return>", lambda e: self._xu_ly_dang_nhap())

    def _dung_tab_tao_tai_khoan(self, cha):
        self.ent_dk_ten = self._them_o_nhap(cha, "Tên đăng nhập", self.var_dk_ten)
        self._them_o_nhap(cha, "Họ và tên", self.var_dk_ho_ten)
        self._them_o_nhap(cha, "Email", self.var_dk_email)
        self._them_o_nhap(cha, "Mật khẩu (tối thiểu 6 ký tự)", self.var_dk_mk, an_chu=True)
        ent_mk2 = self._them_o_nhap(cha, "Nhập lại mật khẩu", self.var_dk_mk2, an_chu=True)

        ttk.Button(cha, text="Tạo tài khoản", style="Chinh.TButton",
                   command=self._xu_ly_tao_tai_khoan).pack(fill="x", pady=(16, 0))
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

        # Kiểm tra nhanh ở UI, các luật còn lại để backend kiểm tra
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

        # Backend của Khoa chưa có hàm dang_ky thì báo rõ thay vì để app lỗi
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
        self.tabs.select(0)
        self.ent_dn_mk.focus_set()

    def _thoat(self):
        """Đóng cửa sổ đăng nhập = thoát luôn ứng dụng (có hỏi xác nhận)."""
        if messagebox.askokcancel("Thoát", "Bạn có chắc muốn thoát ứng dụng?", parent=self):
            self.master.destroy()