"""SidebarComponent: Thanh điều hướng bên trái chứa danh sách dự án, bộ lọc nhanh và profile."""
import tkinter as tk
import customtkinter as ctk

from ui.styles import theme
from utils.helpers import tao_chu_viet_tat


class SidebarComponent(tk.Frame):
    """
    Thanh menu bên trái ứng dụng:
    - Khu vực 1: Logo/Thương hiệu 'Workspace' + Nút co giãn Sidebar '<<'/'>>'
    - Khu vực 2: Danh sách Bộ lọc nhanh
    - Khu vực 3: Danh sách Dự án với vạch chọn, mã DA, badge số lượng bên trái và tên
    - Khu vực 4: Profile người dùng + Nút đăng xuất
    - Thanh Splitter kéo chuột thay đổi chiều rộng linh hoạt
    """

    def __init__(self, master, ql, khi_chon_du_an=None, khi_tao_du_an=None,
                 khi_chon_loc_nhanh=None, khi_dang_xuat=None,
                 khi_thay_doi_trang_thai=None, khi_doi_mat_khau=None):
        super().__init__(master, bg="#ffffff", width=218)
        self.pack_propagate(False)

        self.ql = ql
        self.khi_chon_du_an = khi_chon_du_an
        self.khi_tao_du_an = khi_tao_du_an
        self.khi_chon_loc_nhanh = khi_chon_loc_nhanh
        self.khi_dang_xuat = khi_dang_xuat
        self.khi_thay_doi_trang_thai = khi_thay_doi_trang_thai
        self.khi_doi_mat_khau = khi_doi_mat_khau

        self._ds_du_an = []
        self._ma_du_an_hien_tai = None
        self._ds_item_da = []
        self.nut_loc_nhanh = {}
        self._sidebar_da_thu = False
        self._chieu_rong_cu = 218

        self._dung_giao_dien()

    def _dung_giao_dien(self):
        """Khởi tạo toàn bộ giao diện thanh sidebar và thanh kéo giãn."""
        self.noi_dung = tk.Frame(self, bg="#ffffff")
        self.noi_dung.pack(fill="both", expand=True)

        # Header: Workspace + Nút thu gọn
        vung_dau = tk.Frame(self.noi_dung, bg="#ffffff", padx=10, pady=10)
        vung_dau.pack(fill="x")

        the_logo = tk.Frame(
            vung_dau, bg="#e9e8f4", width=30, height=30,
            highlightthickness=1, highlightbackground="#d2d1df"
        )
        the_logo.pack(side="left", padx=(0, 8))
        the_logo.pack_propagate(False)
        ctk.CTkLabel(
            the_logo, text="|||", text_color="#6d669b",
            font=theme.FONT_DAM, bg_color="#e9e8f4"
        ).place(relx=0.5, rely=0.5, anchor="center")

        thong_tin_ws = tk.Frame(vung_dau, bg="#ffffff")
        thong_tin_ws.pack(side="left", fill="both", expand=True)
        tk.Label(
            thong_tin_ws, text="Workspace", bg="#ffffff",
            fg="#1e1b33", font=theme.FONT_DAM, anchor="w"
        ).pack(fill="x")
        tk.Label(
            thong_tin_ws, text="Quản lý công việc", bg="#ffffff",
            fg="#6d669b", font=theme.FONT_NHO, anchor="w"
        ).pack(fill="x")

        self.btn_thu_sidebar = ctk.CTkButton(
            vung_dau, text="<<", command=self.chuyen_thu_phong,
            width=24, height=22, corner_radius=0,
            fg_color="#e9e8f4", hover_color="#d2d1df",
            border_width=1, border_color="#d2d1df",
            text_color="#6d669b", font=theme.FONT_NHO_DAM
        )
        self.btn_thu_sidebar.pack(side="right")

        tk.Frame(self.noi_dung, bg="#e2e8f0", height=1).pack(fill="x")

        # Bộ lọc nhanh
        vung_loc = tk.Frame(self.noi_dung, bg="#ffffff", padx=10, pady=8)
        vung_loc.pack(fill="x")

        tk.Label(
            vung_loc, text="BỘ LỌC NHANH", bg="#ffffff",
            fg="#94a3b8", font=theme.FONT_NHO_DAM, anchor="w"
        ).pack(fill="x", pady=(0, 4), padx=4)

        danh_sach_loc = [
            ("tat_ca", "Tất cả việc"),
            ("cua_toi", "Việc của tôi"),
            ("khan_cap", "Khẩn cấp & Quá hạn"),
            ("hoan_thanh", "Đã hoàn thành"),
        ]
        for ma_loc, ten_loc in danh_sach_loc:
            btn = ctk.CTkButton(
                vung_loc, text=ten_loc,
                command=lambda k=ma_loc: self._khi_bam_loc(k),
                height=30, corner_radius=0, anchor="w",
                fg_color="#e9e8f4" if ma_loc == "tat_ca" else "transparent",
                border_width=1 if ma_loc == "tat_ca" else 0,
                border_color="#d2d1df" if ma_loc == "tat_ca" else "#ffffff",
                hover_color="#f7f6fb",
                text_color="#6d669b" if ma_loc == "tat_ca" else "#474461",
                font=theme.FONT_NHO_DAM
            )
            btn.pack(fill="x", pady=2)
            self.nut_loc_nhanh[ma_loc] = btn

        tk.Frame(self.noi_dung, bg="#e2e8f0", height=1).pack(fill="x", pady=4)

        # Danh sách dự án
        vung_da = tk.Frame(self.noi_dung, bg="#ffffff", padx=10, pady=8)
        vung_da.pack(fill="both", expand=True)

        dau_da = tk.Frame(vung_da, bg="#ffffff")
        dau_da.pack(fill="x", pady=(0, 6))

        tk.Label(
            dau_da, text="DỰ ÁN", bg="#ffffff", fg="#94a3b8",
            font=theme.FONT_NHO_DAM, anchor="w"
        ).pack(side="left", padx=4)

        la_qt = bool(self.ql.nguoi_dung_hien_tai and self.ql.nguoi_dung_hien_tai.vai_tro == "quan_tri")
        self.btn_tao_da = ctk.CTkButton(
            dau_da, text="+ Mới",
            command=self._khi_bam_tao_da,
            width=50, height=22, corner_radius=0,
            fg_color="#f1f5f9" if la_qt else "#f8fafc",
            hover_color="#e2e8f0", border_width=1,
            border_color="#cbd5e1" if la_qt else "#e2e8f0",
            text_color="#0f172a" if la_qt else "#94a3b8",
            font=theme.FONT_NHO_DAM, state="normal" if la_qt else "disabled"
        )
        self.btn_tao_da.pack(side="right")

        self.khung_ds_da = tk.Frame(vung_da, bg="#ffffff")
        self.khung_ds_da.pack(fill="both", expand=True)

        tk.Frame(self.noi_dung, bg="#e2e8f0", height=1).pack(fill="x")

        # Profile người dùng ở đáy
        vung_day = tk.Frame(self.noi_dung, bg="#ffffff", padx=10, pady=10)
        vung_day.pack(side="bottom", fill="x")

        nd = self.ql.nguoi_dung_hien_tai
        ten_nd = (nd.ho_ten or nd.ten_dang_nhap) if nd else "Khách"
        self.the_user = tk.Frame(
            vung_day, bg="#f8fafc", padx=8, pady=8, cursor="hand2",
            highlightthickness=1, highlightbackground="#e2e8f0"
        )
        self.the_user.pack(fill="x")

        lbl_avatar = ctk.CTkLabel(
            self.the_user, text=tao_chu_viet_tat(ten_nd),
            width=28, height=28, corner_radius=0,
            fg_color=theme.mau_avatar(nd.ten_dang_nhap if nd else ""),
            text_color="white", font=theme.FONT_NHO_DAM
        )
        lbl_avatar.pack(side="left", padx=(0, 6))

        thong_tin = tk.Frame(self.the_user, bg="#f8fafc", cursor="hand2")
        thong_tin.pack(side="left", fill="x", expand=True)

        lbl_ten = tk.Label(
            thong_tin, text=ten_nd, bg="#f8fafc", fg="#0f172a",
            font=theme.FONT_NHO_DAM, anchor="w",
            wraplength=105, justify="left", cursor="hand2"
        )
        lbl_ten.pack(fill="x")
        lbl_vai_tro = tk.Label(
            thong_tin, text="Quản trị viên" if la_qt else "Thành viên",
            bg="#f8fafc", fg="#64748b", font=theme.FONT_NHO, anchor="w", cursor="hand2"
        )
        lbl_vai_tro.pack(fill="x")

        # Nút mũi tên / 3 chấm biểu thị menu
        lbl_menu_icon = tk.Label(
            self.the_user, text="⋮", bg="#f8fafc", fg="#64748b",
            font=theme.FONT_DAM, cursor="hand2", padx=4
        )
        lbl_menu_icon.pack(side="right")

        # Menu popup 2 lựa chọn: Đổi mật khẩu hoặc Thoát
        self.menu_profile = tk.Menu(self, tearoff=0, font=theme.FONT_CHUAN)
        self.menu_profile.add_command(label="🔑 Đổi mật khẩu...", command=self._khi_bam_doi_mat_khau)
        self.menu_profile.add_separator()
        self.menu_profile.add_command(label="🚪 Thoát (Đăng xuất)", command=self._khi_bam_dang_xuat)

        # Gắn sự kiện click mở menu
        for w in (self.the_user, thong_tin, lbl_ten, lbl_vai_tro, lbl_menu_icon):
            w.bind("<Button-1>", self._hien_menu_profile)

        # Hiệu ứng hover
        def _on_enter(_e):
            for widget in (self.the_user, thong_tin, lbl_ten, lbl_vai_tro, lbl_menu_icon):
                widget.configure(bg="#f1f5f9")
            self.the_user.configure(highlightbackground="#cbd5e1")

        def _on_leave(_e):
            for widget in (self.the_user, thong_tin, lbl_ten, lbl_vai_tro, lbl_menu_icon):
                widget.configure(bg="#f8fafc")
            self.the_user.configure(highlightbackground="#e2e8f0")

        self.the_user.bind("<Enter>", _on_enter)
        self.the_user.bind("<Leave>", _on_leave)

        self.bind("<Configure>", self._khi_doi_kich_thuoc)

    def _hien_menu_profile(self, event=None):
        """Hiển thị menu 2 lựa chọn tại vị trí thẻ profile."""
        if event:
            x = event.x_root
            y = event.y_root
        else:
            x = self.the_user.winfo_rootx()
            y = self.the_user.winfo_rooty()
        self.menu_profile.tk_popup(x, y)

    def _khi_bam_loc(self, ma_loc):
        if self.khi_chon_loc_nhanh:
            self.khi_chon_loc_nhanh(ma_loc)

    def _khi_bam_tao_da(self):
        if self.khi_tao_du_an:
            self.khi_tao_du_an()

    def _khi_bam_dang_xuat(self):
        if self.khi_dang_xuat:
            self.khi_dang_xuat()

    def _khi_bam_doi_mat_khau(self):
        if self.khi_doi_mat_khau:
            self.khi_doi_mat_khau()

    def chuyen_thu_phong(self):
        """Bật/tắt trạng thái thu gọn Sidebar."""
        if not self._sidebar_da_thu:
            self._chieu_rong_cu = max(self.winfo_width(), 160)
            self.configure(width=48)
            self.noi_dung.pack_forget()
            self.btn_thu_sidebar.configure(text=">>")
            self._sidebar_da_thu = True
        else:
            self.configure(width=self._chieu_rong_cu)
            self.noi_dung.pack(fill="both", expand=True)
            self.btn_thu_sidebar.configure(text="<<")
            self._sidebar_da_thu = False

    def cap_nhat_loc_nhanh(self, ma_loc_hien_tai):
        """Đánh dấu nút bộ lọc nhanh đang chọn."""
        for ma, btn in self.nut_loc_nhanh.items():
            if ma == ma_loc_hien_tai:
                btn.configure(
                    fg_color="#e9e8f4", border_width=1,
                    border_color="#d2d1df", text_color="#6d669b"
                )
            else:
                btn.configure(
                    fg_color="transparent", border_width=0,
                    border_color="#ffffff", text_color="#474461"
                )

    def cap_nhat_du_an(self, ds_du_an, ma_du_an_dang_chon):
        """Làm mới danh sách dự án với số lượng công việc ở bên trái và tên dự án."""
        self._ds_du_an = ds_du_an
        self._ma_du_an_hien_tai = ma_du_an_dang_chon
        self._ds_item_da.clear()

        for c in self.khung_ds_da.winfo_children():
            c.destroy()

        for d in ds_du_an:
            la_chon = (d.ma_du_an == ma_du_an_dang_chon)
            so_viec = len(d.cong_viec)

            mau_nen = "#e9e8f4" if la_chon else "#ffffff"
            mau_vien = "#d2d1df" if la_chon else "#f4f3f8"
            mau_vach = "#6d669b" if la_chon else mau_nen
            mau_ma = "#6d669b" if la_chon else "#8a86a2"
            mau_ten = "#1e1b33" if la_chon else "#38344e"
            mau_badge_nen = "#d2d1df" if la_chon else "#e0e0ec"
            mau_badge_chu = "#2e2a47" if la_chon else "#5c5875"

            item_da = tk.Frame(
                self.khung_ds_da, bg=mau_nen, cursor="hand2",
                highlightthickness=1, highlightbackground=mau_vien
            )
            item_da.pack(fill="x", pady=2)

            # Vạch active
            vach_active = tk.Frame(item_da, bg=mau_vach, width=3)
            vach_active.pack(side="left", fill="y")

            # Khối thông tin: Mã DA -> Badge Số việc -> Tên dự án
            khung_tt = tk.Frame(item_da, bg=mau_nen, cursor="hand2")
            khung_tt.pack(side="left", fill="x", expand=True, padx=(6, 6), pady=5)

            lbl_ma = tk.Label(
                khung_tt, text=d.ma_du_an, bg=mau_nen, fg=mau_ma,
                font=theme.FONT_NHO_DAM, cursor="hand2"
            )
            lbl_ma.pack(side="left", padx=(0, 5))

            lbl_badge = tk.Label(
                khung_tt, text=str(so_viec), width=2,
                bg=mau_badge_nen, fg=mau_badge_chu,
                font=theme.FONT_NHO_DAM, cursor="hand2",
                padx=3, pady=1
            )
            lbl_badge.pack(side="left", padx=(0, 6))

            lbl_ten = tk.Label(
                khung_tt, text=d.ten_du_an, bg=mau_nen, fg=mau_ten,
                font=theme.FONT_NHO_DAM if la_chon else theme.FONT_NHO,
                anchor="w", cursor="hand2"
            )
            lbl_ten.pack(side="left", fill="x", expand=True)

            self._ds_item_da.append({
                "lbl_ten": lbl_ten,
                "ten_goc": d.ten_du_an,
                "la_chon": la_chon,
                "ma_da": d.ma_du_an,
                "so_viec": so_viec,
            })

            def _chon(_e, target=d.ma_du_an):
                if self.khi_chon_du_an:
                    self.khi_chon_du_an(target)

            for w in (item_da, khung_tt, lbl_ma, lbl_badge, lbl_ten):
                w.bind("<Button-1>", _chon)

        self._tinh_chinh_nhan_du_an()

    def _tinh_chinh_nhan_du_an(self):
        """Cắt tỉa chuỗi tên dự án nếu không gian bề ngang bị hẹp (thêm dấu …)."""
        w = self.winfo_width()
        if w <= 1:
            w = 218
        # Chiều rộng dành cho nhãn tên = w - lề - vạch(3) - mã(45) - badge(20) - lề(40)
        w_ten = max(w - 110, 40)
        # Giả định trung bình 1 ký tự rộng khoảng 7-8px
        max_chars = max(int(w_ten / 7.5), 4)

        for it in self._ds_item_da:
            ten = it["ten_goc"]
            lbl = it["lbl_ten"]
            if not lbl.winfo_exists():
                continue
            if len(ten) > max_chars:
                lbl.configure(text=ten[:max(max_chars - 2, 1)].rstrip() + "…")
            else:
                lbl.configure(text=ten)

    def _khi_doi_kich_thuoc(self, _event=None):
        self._tinh_chinh_nhan_du_an()
