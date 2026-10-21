"""Cửa sổ chính: menu, header Figma, thanh công cụ lọc, bảng Kanban, thanh trạng thái."""
import tkinter as tk
from tkinter import messagebox, simpledialog
import customtkinter as ctk

from ui.du_an_dialog import TaoDuAnDialog, ThanhVienDuAnDialog
from ui.thong_ke_window import ThongKeWindow
from exceptions import KanbanException
from ui import theme
from ui.cong_viec_dialog import CongViecDialog
from ui.cot_kanban import CotKanban
from ui.tien_ich import can_giua

TAT_CA = "Tất cả"


class MainWindow(tk.Toplevel):
    def __init__(self, master, ql, khi_dang_xuat):
        super().__init__(master)
        self.cua_so_thong_ke = None
        self._the_ma = None
        self.ql = ql
        self.khi_dang_xuat = khi_dang_xuat
        self.ds_du_an = []
        self.du_an = None
        self.cac_cot = {}              # {ten_cot: CotKanban}
        self.cv_dang_chon = None
        self.the_dang_chon = None

        self.title("Kanban Workspace - Quản lý công việc")
        self.configure(bg=theme.MAU_NEN)
        self.minsize(980, 560)
        self.protocol("WM_DELETE_WINDOW", self.thoat)

        self.var_du_an = tk.StringVar()
        self.var_tu_khoa = tk.StringVar()
        self.var_uu_tien = tk.StringVar(value=TAT_CA)
        self.var_thanh_vien = tk.StringVar(value=TAT_CA)

        # Thứ tự pack: menu, header Figma, thanh công cụ, thanh trạng thái dưới, bảng Kanban ở giữa
        self._dung_menu()
        self._dung_header_chinh()
        self._dung_thanh_cong_cu()
        self._dung_thanh_trang_thai()
        self._dung_bang_kanban()
        self._dung_menu_chuot_phai()

        self._nap_du_an()
        can_giua(self, 1260, 720)

    # ------------------------------------------------------------ dựng giao diện
    def _dung_menu(self):
        thanh = tk.Menu(self)

        m_tep = tk.Menu(thanh, tearoff=0)
        m_tep.add_command(label="Làm mới", accelerator="F5", command=self.ve_lai)
        m_tep.add_separator()
        m_tep.add_command(label="Đăng xuất", command=self.dang_xuat)
        m_tep.add_command(label="Thoát", command=self.thoat)
        thanh.add_cascade(label="Tệp", menu=m_tep)

        self.m_da = tk.Menu(thanh, tearoff=0)
        self.m_da.add_command(label="Tạo dự án mới...", command=self.tao_du_an)
        self.m_da.add_command(label="Quản lý thành viên dự án...",
                              command=self.quan_ly_thanh_vien)
        self.m_da.add_separator()
        self.m_da.add_command(label="Xóa dự án đang mở", command=self.xoa_du_an)
        thanh.add_cascade(label="Dự án", menu=self.m_da)

        if self.ql.nguoi_dung_hien_tai.vai_tro != "quan_tri":
            for vi_tri in (0, 1, 3):
                self.m_da.entryconfig(vi_tri, state="disabled")

        self.m_cv = tk.Menu(thanh, tearoff=0)
        self.m_cv.add_command(label="Thêm công việc", accelerator="Ctrl+N",
                              command=self.them_cong_viec)
        self.m_cv.add_command(label="Sửa công việc đang chọn", command=self.sua_dang_chon)
        self.m_cv.add_command(label="Xóa công việc đang chọn", command=self.xoa_dang_chon)
        thanh.add_cascade(label="Công việc", menu=self.m_cv)

        m_tk = tk.Menu(thanh, tearoff=0)
        m_tk.add_command(label="Biểu đồ & cảnh báo", accelerator="Ctrl+T",
                         command=self.mo_thong_ke)
        thanh.add_cascade(label="Thống kê", menu=m_tk)

        self.bind("<Control-t>", lambda e: self.mo_thong_ke())
        self.configure(menu=thanh)
        self.bind("<F5>", lambda e: self.ve_lai())
        self.bind("<Control-n>", lambda e: self.them_cong_viec())

        if not self.ql.nguoi_dung_hien_tai.co_quyen_xoa_cong_viec():
            self.m_cv.entryconfig("Xóa công việc đang chọn", state="disabled")

    def _dung_header_chinh(self):
        """Thanh Header màu Teal chuẩn thiết kế Figma kèm các nút thao tác nhanh."""
        nd = self.ql.nguoi_dung_hien_tai
        vai_tro_txt = "Quản trị viên" if nd.vai_tro == "quan_tri" else "Thành viên"

        header = tk.Frame(self, bg=theme.MAU_CHINH, height=64)
        header.pack(side="top", fill="x")

        noi_dung = tk.Frame(header, bg=theme.MAU_CHINH)
        noi_dung.pack(fill="x", padx=18, pady=10)

        # Logo 3 thanh Kanban bên trái
        khung_logo = ctk.CTkFrame(noi_dung, width=38, height=38, corner_radius=9,
                                  fg_color="#287870", border_width=1, border_color="#3c8981")
        khung_logo.pack(side="left", padx=(0, 12))
        khung_logo.pack_propagate(False)
        cv_logo = tk.Canvas(khung_logo, width=24, height=22, bg="#287870",
                            highlightthickness=0, bd=0)
        cv_logo.place(relx=0.5, rely=0.5, anchor="center")
        cv_logo.create_rectangle(2, 8, 6, 20, fill="#9bc4c0", width=0)
        cv_logo.create_rectangle(9, 2, 13, 20, fill="#ffffff", width=0)
        cv_logo.create_rectangle(16, 5, 20, 20, fill=theme.MAU_NHAN, width=0)

        khung_chu = tk.Frame(noi_dung, bg=theme.MAU_CHINH)
        khung_chu.pack(side="left")
        tk.Label(khung_chu, text="KANBAN WORKSPACE", bg=theme.MAU_CHINH,
                 fg="#a9d1cd", font=theme.FONT_EYEBROW, anchor="w").pack(anchor="w")
        tk.Label(khung_chu, text="BẢNG QUẢN LÝ CÔNG VIỆC KANBAN", bg=theme.MAU_CHINH,
                 fg="white", font=("Segoe UI", 13, "bold"), anchor="w").pack(anchor="w")

        # Cụm nút nhanh & thông tin tài khoản bên phải
        cum_phai = tk.Frame(noi_dung, bg=theme.MAU_CHINH)
        cum_phai.pack(side="right")

        ctk.CTkButton(
            cum_phai, text="Đăng xuất", command=self.dang_xuat,
            width=86, height=32, corner_radius=6,
            fg_color="#11564f", hover_color="#0d433d",
            border_width=1, border_color="#3c8981",
            text_color="white", font=theme.FONT_NHO
        ).pack(side="right", padx=(8, 0))

        ctk.CTkButton(
            cum_phai, text="📊 Thống kê", command=self.mo_thong_ke,
            width=102, height=32, corner_radius=6,
            fg_color="#25766e", hover_color="#11564f",
            border_width=1, border_color="#3c8981",
            text_color="white", font=theme.FONT_DAM
        ).pack(side="right", padx=(8, 0))

        if nd.vai_tro == "quan_tri":
            ctk.CTkButton(
                cum_phai, text="👥 Thành viên", command=self.quan_ly_thanh_vien,
                width=108, height=32, corner_radius=6,
                fg_color="#25766e", hover_color="#11564f",
                border_width=1, border_color="#3c8981",
                text_color="white", font=theme.FONT_DAM
            ).pack(side="right", padx=(8, 0))

            ctk.CTkButton(
                cum_phai, text="+ Dự án mới", command=self.tao_du_an,
                width=102, height=32, corner_radius=6,
                fg_color="#25766e", hover_color="#11564f",
                border_width=1, border_color="#3c8981",
                text_color=theme.MAU_NHAN, font=theme.FONT_DAM
            ).pack(side="right", padx=(8, 0))

        tk.Label(
            cum_phai,
            text=f"👤 {nd.ho_ten or nd.ten_dang_nhap} ({vai_tro_txt})",
            bg=theme.MAU_CHINH, fg="#e4f3f0", font=theme.FONT_DAM
        ).pack(side="right", padx=(0, 8))

    def _dung_thanh_cong_cu(self):
        khung_tc = ctk.CTkFrame(
            self, fg_color=theme.MAU_THE, corner_radius=10,
            border_width=1, border_color=theme.MAU_VIEN
        )
        khung_tc.pack(side="top", fill="x", padx=12, pady=(10, 8))

        tc = tk.Frame(khung_tc, bg=theme.MAU_THE, padx=14, pady=10)
        tc.pack(fill="x")
        tc.columnconfigure(3, weight=1)

        tk.Label(tc, text="Dự án:", bg=theme.MAU_THE, fg=theme.MAU_CHU_NHAN,
                 font=theme.FONT_DAM).grid(row=0, column=0, padx=(0, 6))
        self.cbb_du_an = ctk.CTkComboBox(
            tc, variable=self.var_du_an, values=[],
            command=self._khi_doi_du_an, state="readonly",
            width=250, height=36, corner_radius=6,
            fg_color=theme.MAU_O_NHAP, border_color=theme.MAU_VIEN_THE, border_width=1,
            button_color=theme.MAU_VIEN_THE, button_hover_color=theme.MAU_CHINH_NHAT,
            text_color=theme.MAU_CHU, font=theme.FONT_DAM
        )
        self.cbb_du_an.grid(row=0, column=1, padx=(0, 14))

        tk.Label(tc, text="Tìm kiếm:", bg=theme.MAU_THE, fg=theme.MAU_CHU_NHAN,
                 font=theme.FONT_DAM).grid(row=0, column=2, padx=(0, 6))
        self.ent_tim = ctk.CTkEntry(
            tc, textvariable=self.var_tu_khoa,
            placeholder_text="Nhập tiêu đề hoặc mô tả công việc...",
            height=36, corner_radius=6, fg_color=theme.MAU_O_NHAP,
            border_color=theme.MAU_VIEN_THE, border_width=1,
            text_color=theme.MAU_CHU, font=theme.FONT_CHUAN
        )
        self.ent_tim.grid(row=0, column=3, sticky="ew", padx=(0, 14))
        self.ent_tim.bind("<KeyRelease>", lambda e: self.ve_lai())

        tk.Label(tc, text="Ưu tiên:", bg=theme.MAU_THE, fg=theme.MAU_CHU_NHAN,
                 font=theme.FONT_DAM).grid(row=0, column=4, padx=(0, 6))
        self.cbb_ut = ctk.CTkComboBox(
            tc, variable=self.var_uu_tien,
            values=[TAT_CA, "Thấp", "Trung bình", "Cao", "Khẩn"],
            command=lambda _: self.ve_lai(), state="readonly",
            width=125, height=36, corner_radius=6,
            fg_color=theme.MAU_O_NHAP, border_color=theme.MAU_VIEN_THE, border_width=1,
            button_color=theme.MAU_VIEN_THE, button_hover_color=theme.MAU_CHINH_NHAT,
            text_color=theme.MAU_CHU, font=theme.FONT_CHUAN
        )
        self.cbb_ut.grid(row=0, column=5, padx=(0, 14))

        tk.Label(tc, text="Thành viên:", bg=theme.MAU_THE, fg=theme.MAU_CHU_NHAN,
                 font=theme.FONT_DAM).grid(row=0, column=6, padx=(0, 6))
        self.cbb_tv = ctk.CTkComboBox(
            tc, variable=self.var_thanh_vien, values=[TAT_CA],
            command=lambda _: self.ve_lai(), state="readonly",
            width=125, height=36, corner_radius=6,
            fg_color=theme.MAU_O_NHAP, border_color=theme.MAU_VIEN_THE, border_width=1,
            button_color=theme.MAU_VIEN_THE, button_hover_color=theme.MAU_CHINH_NHAT,
            text_color=theme.MAU_CHU, font=theme.FONT_CHUAN
        )
        self.cbb_tv.grid(row=0, column=7, padx=(0, 14))

        ctk.CTkButton(
            tc, text="+ Thêm công việc", command=self.them_cong_viec,
            width=142, height=36, corner_radius=7,
            fg_color=theme.MAU_CHINH, hover_color=theme.MAU_CHINH_DAM,
            text_color="white", font=theme.FONT_DAM
        ).grid(row=0, column=8)

    def _dung_thanh_trang_thai(self):
        khung_duoi = tk.Frame(self, bg=theme.MAU_THE, bd=0, highlightthickness=1,
                              highlightbackground=theme.MAU_VIEN)
        khung_duoi.pack(side="bottom", fill="x")
        self.lbl_trang_thai = tk.Label(
            khung_duoi, anchor="w", bg=theme.MAU_THE, fg=theme.MAU_CHU_NHAN,
            font=theme.FONT_NHO, padx=14, pady=5
        )
        self.lbl_trang_thai.pack(side="left", fill="x", expand=True)

        tk.Label(
            khung_duoi,
            text="Mẹo: Kéo-thả thẻ để chuyển cột • Double-click để sửa • Chuột phải để mở menu",
            bg=theme.MAU_THE, fg=theme.MAU_CHU_PHU, font=theme.FONT_NHO, padx=14
        ).pack(side="right")

    def _dung_bang_kanban(self):
        self.bang = tk.Frame(self, bg=theme.MAU_NEN)
        self.bang.pack(fill="both", expand=True, padx=8, pady=(0, 10))
        self.bang.rowconfigure(0, weight=1)

    def _dung_menu_chuot_phai(self):
        self.menu_phai = tk.Menu(self, tearoff=0)
        self.menu_phai.add_command(label="Sửa công việc", command=self.sua_dang_chon)
        self.menu_chuyen = tk.Menu(self.menu_phai, tearoff=0)
        self.menu_phai.add_cascade(label="Chuyển sang cột", menu=self.menu_chuyen)
        self.menu_phai.add_separator()
        self.menu_phai.add_command(label="Xóa công việc", command=self.xoa_dang_chon)
        if not self.ql.nguoi_dung_hien_tai.co_quyen_xoa_cong_viec():
            self.menu_phai.entryconfig("Xóa công việc", state="disabled")

    # ------------------------------------------------------------ nạp dữ liệu
    def _nap_du_an(self, chon_ma=None):
        """Nạp lại danh sách dự án vào Combobox."""
        chon_ma = chon_ma or (self.du_an.ma_du_an if self.du_an else None)
        self.ds_du_an = [d for d in self.ql.lay_danh_sach_du_an()
                         if self.ql.kiem_tra_quyen_du_an(d)]
        ds_ten = [f"{d.ma_du_an} - {d.ten_du_an}" for d in self.ds_du_an]
        self.cbb_du_an.configure(values=ds_ten if ds_ten else [""])

        if not self.ds_du_an:
            self.du_an = None
            self.var_du_an.set("")
            self.cbb_tv.configure(values=[TAT_CA])
            self._xoa_cot()
            self.cv_dang_chon = None
            self.the_dang_chon = None
            ck = self.cua_so_thong_ke
            if ck is not None and ck.winfo_exists():
                ck.destroy()
            self.lbl_trang_thai.configure(
                text="Chưa có dự án nào. Quản trị viên có thể tạo ở menu Dự án.")
            return

        vi_tri = next((i for i, d in enumerate(self.ds_du_an) if d.ma_du_an == chon_ma), 0)
        self.var_du_an.set(ds_ten[vi_tri])
        self._khi_doi_du_an()

    def _xoa_cot(self):
        for cot in self.cac_cot.values():
            cot.destroy()
        self.cac_cot.clear()

    def _tao_cot(self):
        self._xoa_cot()
        for i, ten in enumerate(self.du_an.danh_sach_cot):
            cot = CotKanban(self.bang, ten, khi_chon=self.chon_the,
                            khi_mo=self.mo_the, khi_menu=self.hien_menu,
                            khi_keo=self.khi_keo, khi_tha=self.khi_tha)
            cot.grid(row=0, column=i, sticky="nsew", padx=5)
            self.bang.columnconfigure(i, weight=1, uniform="cot")
            self.cac_cot[ten] = cot

    def _lam_moi_thanh_vien(self):
        """Gọi sau khi thêm/xóa thành viên dự án: cập nhật ô lọc thành viên."""
        if self.du_an is None:
            return
        ds_tv = [TAT_CA] + list(self.du_an.thanh_vien_tham_gia)
        self.cbb_tv.configure(values=ds_tv)
        if self.var_thanh_vien.get() not in ds_tv:
            self.var_thanh_vien.set(TAT_CA)
        self.ve_lai()

    def _khi_doi_du_an(self, chon=None):
        chuoi = self.var_du_an.get()
        vi_tri = next(
            (i for i, d in enumerate(self.ds_du_an) if f"{d.ma_du_an} - {d.ten_du_an}" == chuoi),
            0
        )
        self.du_an = self.ds_du_an[vi_tri]
        ds_tv = [TAT_CA] + list(self.du_an.thanh_vien_tham_gia)
        self.cbb_tv.configure(values=ds_tv)
        self.var_thanh_vien.set(TAT_CA)
        self._tao_cot()
        self.ve_lai()

    def tao_du_an(self):
        TaoDuAnDialog(self, self.ql,
                      khi_xong=lambda du_an: self._nap_du_an(chon_ma=du_an.ma_du_an))

    def quan_ly_thanh_vien(self):
        if self.du_an is None:
            messagebox.showinfo("Chưa có dự án", "Hãy tạo hoặc chọn một dự án trước.", parent=self)
            return
        ThanhVienDuAnDialog(self, self.ql, self.du_an, khi_xong=self._lam_moi_thanh_vien)

    def xoa_du_an(self):
        da = self.du_an
        if da is None:
            messagebox.showinfo("Chưa có dự án", "Không có dự án nào để xóa.", parent=self)
            return
        tong = len(da.cong_viec)
        chua_xong = sum(1 for cv in da.cong_viec if not cv.is_hoan_thanh())
        if not messagebox.askyesno(
                "Xác nhận xóa dự án",
                f"Xóa dự án {da.ma_du_an} - {da.ten_du_an}?\n\n"
                f"Sẽ mất vĩnh viễn {tong} công việc và danh sách "
                f"{len(da.thanh_vien_tham_gia)} thành viên.",
                icon="warning", parent=self):
            return
        if chua_xong:
            nhap = simpledialog.askstring(
                "Xác nhận lần 2",
                f"Dự án còn {chua_xong} việc chưa hoàn thành.\n"
                f"Gõ lại mã dự án ({da.ma_du_an}) để xác nhận:", parent=self)
            if nhap is None or nhap.strip().upper() != da.ma_du_an:
                messagebox.showinfo("Đã hủy", "Mã không khớp, dự án chưa bị xóa.", parent=self)
                return
        try:
            self.ql.xoa_du_an(da.ma_du_an)
        except KanbanException as loi:
            messagebox.showerror("Không xóa được", loi.thong_diep, parent=self)
            return
        self._nap_du_an()

    def _cong_viec_sau_loc(self):
        """Giao của 3 bộ lọc: từ khóa, ưu tiên, thành viên (đều gọi hàm của backend)."""
        ql, da = self.ql, self.du_an
        kq = ql.tim_kiem_cong_viec(da, self.var_tu_khoa.get())
        if self.var_uu_tien.get() != TAT_CA:
            ma = {cv.ma_cong_viec for cv in ql.loc_theo_muc_uu_tien(da, self.var_uu_tien.get())}
            kq = [cv for cv in kq if cv.ma_cong_viec in ma]
        if self.var_thanh_vien.get() != TAT_CA:
            ma = {cv.ma_cong_viec for cv in ql.loc_theo_thanh_vien(da, self.var_thanh_vien.get())}
            kq = [cv for cv in kq if cv.ma_cong_viec in ma]
        return kq

    def ve_lai(self):
        if self.du_an is None:
            return
        cong_viec = self._cong_viec_sau_loc()
        for ten, cot in self.cac_cot.items():
            cot.hien_thi([cv for cv in cong_viec if cv.trang_thai == ten])
        self.cv_dang_chon = None
        self.the_dang_chon = None
        nd = self.ql.nguoi_dung_hien_tai
        self.lbl_trang_thai.configure(
            text=f"📁 Dự án: {self.du_an.ma_du_an} - {self.du_an.ten_du_an}   |   "
                 f"Hiển thị: {len(cong_viec)}/{len(self.du_an.cong_viec)} công việc   |   "
                 f"Tiến độ: {self.du_an.tinh_tien_do()}%   |   "
                 f"Phiên: {nd.ho_ten or nd.ten_dang_nhap} ({nd.vai_tro})"
        )
        ck = self.cua_so_thong_ke
        if ck is not None and ck.winfo_exists():
            ck.dat_du_an(self.du_an)

    # ------------------------------------------------------------ sự kiện trên thẻ
    def chon_the(self, cv):
        if self.the_dang_chon is not None and self.the_dang_chon.winfo_exists():
            self.the_dang_chon.dat_chon(False)
        self.cv_dang_chon = cv
        for cot in self.cac_cot.values():
            the = cot.cac_the.get(cv.ma_cong_viec)
            if the:
                the.dat_chon(True)
                self.the_dang_chon = the

    def mo_the(self, cv):
        self.chon_the(cv)
        self.sua_dang_chon()

    def hien_menu(self, cv, event):
        self.chon_the(cv)
        self.menu_chuyen.delete(0, "end")
        for ten in self.du_an.danh_sach_cot:
            if ten != cv.trang_thai:
                self.menu_chuyen.add_command(
                    label=ten, command=lambda t=ten: self.chuyen_cot(cv, t))
        try:
            self.menu_phai.tk_popup(event.x_root, event.y_root)
        finally:
            self.menu_phai.grab_release()

    # ------------------------------------------------------------ thao tác
    def them_cong_viec(self):
        if self.du_an is None:
            return
        CongViecDialog(self, self.ql, self.du_an, khi_xong=self.ve_lai)

    def sua_dang_chon(self):
        if self.cv_dang_chon is None:
            messagebox.showinfo("Chưa chọn", "Hãy bấm chọn một thẻ công việc trước.", parent=self)
            return
        CongViecDialog(self, self.ql, self.du_an, self.cv_dang_chon, khi_xong=self.ve_lai)

    def chuyen_cot(self, cv, ten_cot):
        try:
            self.ql.chuyen_trang_thai(self.du_an, cv.ma_cong_viec, ten_cot)
        except KanbanException as loi:
            messagebox.showerror("Không chuyển được", loi.thong_diep, parent=self)
            return
        self.ve_lai()
        self.chon_the(cv)

    def xoa_dang_chon(self):
        cv = self.cv_dang_chon
        if cv is None:
            messagebox.showinfo("Chưa chọn", "Hãy bấm chọn một thẻ công việc trước.", parent=self)
            return
        if not messagebox.askyesno(
                "Xác nhận xóa",
                f"Xóa công việc {cv.ma_cong_viec} - {cv.tieu_de}?\nKhông thể hoàn tác.",
                icon="warning", parent=self):
            return
        try:
            self.ql.xoa_cong_viec(self.du_an, cv.ma_cong_viec)
        except KanbanException as loi:
            messagebox.showerror("Không xóa được", loi.thong_diep, parent=self)
            return
        self.ve_lai()

    def mo_thong_ke(self):
        if self.du_an is None:
            return
        ck = self.cua_so_thong_ke
        if ck is not None and ck.winfo_exists():
            ck.dat_du_an(self.du_an)
            ck.lift()
            return
        self.cua_so_thong_ke = ThongKeWindow(self, self.du_an)

    def dang_xuat(self):
        if messagebox.askyesno("Đăng xuất", "Bạn có chắc muốn đăng xuất?", parent=self):
            self.ql.dang_xuat()
            self.destroy()
            self.khi_dang_xuat()

    def thoat(self):
        if messagebox.askokcancel("Thoát", "Bạn có chắc muốn thoát ứng dụng?", parent=self):
            self.master.destroy()

    def _cot_duoi_chuot(self, event):
        """Tên cột đang nằm dưới con trỏ (None nếu thả ra ngoài)."""
        for ten, cot in self.cac_cot.items():
            if cot.chua_diem(event.x_root, event.y_root):
                return ten
        return None

    def khi_keo(self, cv, event):
        """Gọi liên tục khi đang kéo: cho nhãn 'bóng' chạy theo chuột, tô sáng cột đích."""
        if self._the_ma is None:
            self._the_ma = tk.Label(self, bg=theme.MAU_CHINH, fg="white",
                                    font=theme.FONT_DAM, padx=12, pady=6)
        self._the_ma.configure(text=f"✥  {cv.ma_cong_viec} — {cv.tieu_de}")
        self._the_ma.place(x=event.x_root - self.winfo_rootx() + 12,
                           y=event.y_root - self.winfo_rooty() + 12)
        self._the_ma.lift()

        dich = self._cot_duoi_chuot(event)
        for ten, cot in self.cac_cot.items():
            cot.to_sang(ten == dich and ten != cv.trang_thai)

    def khi_tha(self, cv, event):
        if self._the_ma is not None:
            self._the_ma.place_forget()
        for cot in self.cac_cot.values():
            cot.to_sang(False)
        dich = self._cot_duoi_chuot(event)
        if dich and dich != cv.trang_thai:
            self.after(10, lambda: self.chuyen_cot(cv, dich))
