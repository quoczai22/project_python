"""TopbarComponent: Thanh tiêu đề trên, bộ lọc tìm kiếm và các nút tác vụ dự án."""
import tkinter as tk
from tkinter import ttk
import customtkinter as ctk

from ui.styles import theme

TAT_CA = "Tất cả"


class TopbarComponent(tk.Frame):
    """
    Thanh điều hướng phía trên của màn hình làm việc:
    - Breadcrumb và tên dự án lớn
    - Cụm nút hành động: Thêm việc (+ 135px), Hoạt động, Thống kê, Thành viên, Xóa dự án
    - Hàng tìm kiếm và lọc: Ô nhập tìm kiếm, dropdown ưu tiên, dropdown thành viên, nút đặt lại
    - SegmentedButton chuyển chế độ (Bảng Kanban / Danh sách) kèm thanh tiến độ hoàn thành
    """

    def __init__(self, master,
                 khi_them_viec=None, khi_bat_tat_hoat_dong=None,
                 khi_mo_thong_ke=None, khi_ql_thanh_vien=None,
                 khi_xoa_du_an=None, khi_thay_doi_loc=None,
                 khi_dat_lai_loc=None, khi_doi_che_do=None):
        super().__init__(master, bg=theme.MAU_NEN)

        self.khi_them_viec = khi_them_viec
        self.khi_bat_tat_hoat_dong = khi_bat_tat_hoat_dong
        self.khi_mo_thong_ke = khi_mo_thong_ke
        self.khi_ql_thanh_vien = khi_ql_thanh_vien
        self.khi_xoa_du_an = khi_xoa_du_an
        self.khi_thay_doi_loc = khi_thay_doi_loc
        self.khi_dat_lai_loc = khi_dat_lai_loc
        self.khi_doi_che_do = khi_doi_che_do

        self.var_tim_kiem = tk.StringVar()
        self.var_uu_tien = tk.StringVar(value=TAT_CA)
        self.var_thanh_vien = tk.StringVar(value=TAT_CA)

        self._dung_giao_dien()

    def _dung_giao_dien(self):
        """Khởi tạo Header dự án, Toolbar lọc và thanh chuyển tab."""
        # 1. Header dự án
        khung_dau = tk.Frame(self, bg=theme.MAU_NEN, padx=16, pady=8)
        khung_dau.pack(fill="x")

        # Cụm nút bên phải (pack trước với side='right' để giữ chỗ cố định)
        cum_nut = tk.Frame(khung_dau, bg=theme.MAU_NEN)
        cum_nut.pack(side="right", padx=(12, 0))

        self.btn_them_cv = ctk.CTkButton(
            cum_nut, text="+ Thêm công việc",
            command=self._khi_bam_them_cv,
            width=140, height=32, corner_radius=0,
            fg_color="#6d669b", hover_color="#595284",
            text_color="#ffffff", font=theme.FONT_NHO_DAM
        )
        self.btn_them_cv.pack(side="left", padx=(0, 6))

        self.btn_hoat_dong = ctk.CTkButton(
            cum_nut, text="Hoạt động",
            command=self._khi_bam_hoat_dong,
            width=80, height=32, corner_radius=0,
            fg_color="#ffffff", hover_color="#f1f5f9",
            border_width=1, border_color="#cbd5e1",
            text_color="#0f172a", font=theme.FONT_NHO_DAM
        )
        self.btn_hoat_dong.pack(side="left", padx=(0, 6))

        self.btn_thong_ke = ctk.CTkButton(
            cum_nut, text="Thống kê",
            command=self._khi_bam_thong_ke,
            width=80, height=32, corner_radius=0,
            fg_color="#ffffff", hover_color="#f1f5f9",
            border_width=1, border_color="#cbd5e1",
            text_color="#0f172a", font=theme.FONT_NHO_DAM
        )
        self.btn_thong_ke.pack(side="left", padx=(0, 6))

        self.btn_thanh_vien = ctk.CTkButton(
            cum_nut, text="Thành viên",
            command=self._khi_bam_thanh_vien,
            width=85, height=32, corner_radius=0,
            fg_color="#ffffff", hover_color="#f1f5f9",
            border_width=1, border_color="#cbd5e1",
            text_color="#0f172a", font=theme.FONT_NHO_DAM
        )
        self.btn_thanh_vien.pack(side="left", padx=(0, 6))

        self.btn_xoa_da = ctk.CTkButton(
            cum_nut, text="Xóa dự án",
            command=self._khi_bam_xoa_da,
            width=80, height=32, corner_radius=0,
            fg_color="#fee2e2", hover_color="#fecaca",
            border_width=1, border_color="#fca5a5",
            text_color="#dc2626", font=theme.FONT_NHO_DAM
        )
        self.btn_xoa_da.pack(side="left")

        # Cụm thông tin bên trái
        ben_trai = tk.Frame(khung_dau, bg=theme.MAU_NEN)
        ben_trai.pack(side="left", fill="x", expand=True)

        tk.Label(
            ben_trai, text="Dự án / Quản lý tiến độ",
            bg=theme.MAU_NEN, fg="#64748b",
            font=theme.FONT_NHO, anchor="w"
        ).pack(anchor="w")

        self.lbl_ten_da = tk.Label(
            ben_trai, text="Chưa có dự án nào",
            bg=theme.MAU_NEN, fg="#0f172a",
            font=theme.FONT_TIEU_DE, anchor="w"
        )
        self.lbl_ten_da.pack(anchor="w", pady=(2, 0))

        # 2. Thanh tìm kiếm và bộ lọc
        hang_loc = tk.Frame(self, bg=theme.MAU_NEN, padx=16, pady=4)
        hang_loc.pack(fill="x")

        hang_loc.columnconfigure(0, weight=1)

        self.entry_tim = ctk.CTkEntry(
            hang_loc,
            placeholder_text="Tìm kiếm công việc...",
            textvariable=self.var_tim_kiem,
            height=34, corner_radius=0,
            border_width=1, border_color="#cbd5e1",
            fg_color="#ffffff", text_color="#0f172a",
            placeholder_text_color="#94a3b8", font=theme.FONT_CHUAN
        )
        self.entry_tim.grid(row=0, column=0, sticky="ew", padx=(0, 8))
        self.entry_tim.bind("<KeyRelease>", lambda _e: self._bao_loc_thay_doi())

        self.cbb_uu_tien = ctk.CTkComboBox(
            hang_loc,
            values=[TAT_CA, "Thấp", "Trung bình", "Cao", "Khẩn"],
            variable=self.var_uu_tien,
            command=lambda _: self._bao_loc_thay_doi(),
            width=118, height=34, corner_radius=0,
            border_width=1, border_color="#cbd5e1",
            fg_color="#ffffff", text_color="#0f172a",
            button_color="#cbd5e1", button_hover_color="#94a3b8",
            dropdown_fg_color="#ffffff", font=theme.FONT_CHUAN
        )
        self.cbb_uu_tien.grid(row=0, column=1, padx=(0, 6))

        self.cbb_tv = ctk.CTkComboBox(
            hang_loc,
            values=[TAT_CA],
            variable=self.var_thanh_vien,
            command=lambda _: self._bao_loc_thay_doi(),
            width=128, height=34, corner_radius=0,
            border_width=1, border_color="#cbd5e1",
            fg_color="#ffffff", text_color="#0f172a",
            button_color="#cbd5e1", button_hover_color="#94a3b8",
            dropdown_fg_color="#ffffff", font=theme.FONT_CHUAN
        )
        self.cbb_tv.grid(row=0, column=2, padx=(0, 6))

        self.btn_dat_lai = ctk.CTkButton(
            hang_loc, text="Đặt lại",
            command=self._khi_bam_dat_lai,
            width=72, height=34, corner_radius=0,
            fg_color="#ffffff", hover_color="#f1f5f9",
            border_width=1, border_color="#cbd5e1",
            text_color="#64748b", font=theme.FONT_NHO_DAM
        )
        self.btn_dat_lai.grid(row=0, column=3)

        # 3. Tab chế độ xem và thanh tiến độ
        khung_tab = tk.Frame(self, bg=theme.MAU_NEN, padx=16)
        khung_tab.pack(fill="x", pady=(4, 6))

        self.seg_che_do = ctk.CTkSegmentedButton(
            khung_tab,
            values=["Bảng Kanban", "Danh sách", "Chờ duyệt", "Đã hủy"],
            command=self._khi_chuyen_tab,
            font=theme.FONT_NHO_DAM,
            fg_color="#e2e8f0",
            selected_color="#ffffff",
            selected_hover_color="#ffffff",
            unselected_color="#e2e8f0",
            unselected_hover_color="#cbd5e1",
            text_color=theme.MAU_CHU,
            border_width=1,
            height=30,
            corner_radius=0
        )
        self.seg_che_do.pack(side="left")
        self.seg_che_do.set("Bảng Kanban")

        cum_td = tk.Frame(khung_tab, bg=theme.MAU_NEN)
        cum_td.pack(side="right")

        self.thanh_tien_do = ctk.CTkProgressBar(
            cum_td, width=90, height=8, corner_radius=0,
            fg_color="#e0e0ec", progress_color="#6d669b"
        )
        self.thanh_tien_do.pack(side="left", padx=(0, 8))
        self.thanh_tien_do.set(0)

        self.lbl_tien_do = tk.Label(
            cum_td, text="0% (0/0)",
            bg=theme.MAU_NEN, fg="#64748b",
            font=theme.FONT_NHO_DAM
        )
        self.lbl_tien_do.pack(side="left")

    def _khi_bam_them_cv(self):
        if self.khi_them_viec:
            self.khi_them_viec()

    def _khi_bam_hoat_dong(self):
        if self.khi_bat_tat_hoat_dong:
            self.khi_bat_tat_hoat_dong()

    def _khi_bam_thong_ke(self):
        if self.khi_mo_thong_ke:
            self.khi_mo_thong_ke()

    def _khi_bam_thanh_vien(self):
        if self.khi_ql_thanh_vien:
            self.khi_ql_thanh_vien()

    def _khi_bam_xoa_da(self):
        if self.khi_xoa_du_an:
            self.khi_xoa_du_an()

    def _bao_loc_thay_doi(self):
        if self.khi_thay_doi_loc:
            self.khi_thay_doi_loc()

    def _khi_bam_dat_lai(self):
        self.var_tim_kiem.set("")
        self.var_uu_tien.set(TAT_CA)
        self.var_thanh_vien.set(TAT_CA)
        if self.khi_dat_lai_loc:
            self.khi_dat_lai_loc()

    def _khi_chuyen_tab(self, gia_tri):
        if self.khi_doi_che_do:
            self.khi_doi_che_do(gia_tri)

    def cap_nhat_tieu_de(self, ma_da, ten_da):
        """Cập nhật tiêu đề dự án."""
        if ma_da:
            self.lbl_ten_da.configure(text=f"{ma_da} — {ten_da}")
        else:
            self.lbl_ten_da.configure(text=ten_da)

    def cap_nhat_thanh_vien(self, ds_thanh_vien):
        """Cập nhật danh sách thành viên trong dropdown lọc."""
        gia_tri = [TAT_CA] + [f"{tv.ten_dang_nhap} - {tv.ho_ten}" for tv in ds_thanh_vien]
        self.cbb_tv.configure(values=gia_tri)

    def cap_nhat_tien_do(self, tong, xong):
        """Cập nhật thanh tiến độ và nhãn phần trăm."""
        if tong <= 0:
            self.thanh_tien_do.set(0)
            self.lbl_tien_do.configure(text="0% (0/0)")
        else:
            ty_le = min(max(xong / tong, 0.0), 1.0)
            self.thanh_tien_do.set(ty_le)
            self.lbl_tien_do.configure(text=f"{int(ty_le * 100)}% ({xong}/{tong})")
