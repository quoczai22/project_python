"""BoardView: Màn hình chính hiển thị Bảng Kanban, Chế độ Danh sách và Ngăn kéo Hoạt động bên phải."""
import tkinter as tk
from tkinter import ttk
import customtkinter as ctk

from ui.styles import theme
from ui.components.column_widget import ColumnWidget


class BoardView(tk.Frame):
    """
    View chính của không gian làm việc:
    - 4 Thẻ KPI Dashboard tóm tắt
    - Khu vực hiển thị linh hoạt (Grid cột 0: Bảng Kanban hoặc Danh sách; Cột 1: Ngăn kéo Hoạt động bên phải)
    """

    def __init__(self, master,
                 khi_chon_task=None, khi_mo_task=None, khi_menu_task=None,
                 khi_keo_task=None, khi_tha_task=None, khi_them_nhanh=None,
                 khi_chuyen_nhanh=None, khi_dong_hoat_dong=None):
        super().__init__(master, bg="#f1f5f9")

        self.khi_chon_task = khi_chon_task
        self.khi_mo_task = khi_mo_task
        self.khi_menu_task = khi_menu_task
        self.khi_keo_task = khi_keo_task
        self.khi_tha_task = khi_tha_task
        self.khi_them_nhanh = khi_them_nhanh
        self.khi_chuyen_nhanh = khi_chuyen_nhanh
        self.khi_dong_hoat_dong = khi_dong_hoat_dong

        self.cot_widgets = {}  # {ten_cot: ColumnWidget}
        self.che_do_xem = "Bảng Kanban"

        self._dung_giao_dien()

    def _dung_giao_dien(self):
        # 1. 4 Thẻ KPI Summary Cards
        self.khung_kpi = tk.Frame(self, bg="#f1f5f9", padx=16, pady=4)
        self.khung_kpi.pack(fill="x", pady=(2, 6))
        for i in range(4):
            self.khung_kpi.columnconfigure(i, weight=1, uniform="kpi")

        cauhinh_kpi = [
            ("tong", "Tổng công việc", "#0f172a"),
            ("dang_lam", "Đang thực hiện", "#d97706"),
            ("xong", "Đã hoàn thành", "#16a34a"),
            ("khan", "Khẩn & Quá hạn", "#dc2626"),
        ]
        self.lbl_kpis = {}
        for idx, (key, title, col) in enumerate(cauhinh_kpi):
            card = ctk.CTkFrame(
                self.khung_kpi, fg_color="white", corner_radius=0,
                border_width=1, border_color="#e2e8f0", height=60
            )
            card.grid(row=0, column=idx, sticky="ew", padx=(0 if idx == 0 else 3, 0 if idx == 3 else 3))
            card.pack_propagate(False)
            b = tk.Frame(card, bg="white", padx=10, pady=6)
            b.pack(fill="both", expand=True)
            tk.Label(b, text=title, bg="white", fg="#64748b", font=theme.FONT_NHO, anchor="w").pack(anchor="w")
            lbl = tk.Label(b, text="0 việc", bg="white", fg=col, font=theme.FONT_DAM, anchor="w")
            lbl.pack(anchor="w")
            self.lbl_kpis[key] = lbl

        # 2. Khu vực nội dung hai cột (Cột 0: Bảng/Danh sách, Cột 1: Drawer Hoạt động bên phải)
        self.khu_vuc_chinh = tk.Frame(self, bg="#f1f5f9", padx=16, pady=4)
        self.khu_vuc_chinh.pack(fill="both", expand=True)
        self.khu_vuc_chinh.columnconfigure(0, weight=1)
        self.khu_vuc_chinh.rowconfigure(0, weight=1)

        # Container cho Bảng Kanban / Danh sách
        self.container_view = tk.Frame(self.khu_vuc_chinh, bg="#f1f5f9")
        self.container_view.grid(row=0, column=0, sticky="nsew")

        # View 1: Bảng Kanban (Canvas cuộn ngang)
        self.canvas_kanban = tk.Canvas(self.container_view, bg="#f1f5f9", highlightthickness=0)
        self.thanh_cuon_ngang = ttk.Scrollbar(
            self.container_view, orient="horizontal", command=self.canvas_kanban.xview
        )
        self.canvas_kanban.configure(xscrollcommand=self.thanh_cuon_ngang.set)

        self.khung_cac_cot = tk.Frame(self.canvas_kanban, bg="#f1f5f9")
        self._cua_so_kanban = self.canvas_kanban.create_window(
            (0, 0), window=self.khung_cac_cot, anchor="nw"
        )

        self.canvas_kanban.pack(fill="both", expand=True)
        self.khung_cac_cot.bind("<Configure>", self._cap_nhat_vung_cuon_ngang)
        self.canvas_kanban.bind("<Configure>", self._khi_canvas_doi_co)

        # View 2: Danh sách Treeview
        self.khung_danh_sach = tk.Frame(self.container_view, bg="white", highlightthickness=1, highlightbackground="#e2e8f0")
        cac_cot_ds = (
            ("ma", "Mã", 80, "center"),
            ("tieu_de", "Tiêu đề", 280, "w"),
            ("trang_thai", "Trạng thái", 120, "center"),
            ("uu_tien", "Ưu tiên", 100, "center"),
            ("nguoi", "Phụ trách", 130, "w"),
            ("han", "Hạn chót", 110, "center"),
            ("canh_bao", "Cảnh báo", 160, "w"),
        )
        self.tree_ds = ttk.Treeview(
            self.khung_danh_sach, columns=[c[0] for c in cac_cot_ds],
            show="headings", selectmode="browse"
        )
        for k, t, w, a in cac_cot_ds:
            self.tree_ds.heading(k, text=t)
            self.tree_ds.column(k, width=w, anchor=a, stretch=(k == "tieu_de"))

        cuon_doc_ds = ttk.Scrollbar(self.khung_danh_sach, orient="vertical", command=self.tree_ds.yview)
        cuon_ngang_ds = ttk.Scrollbar(self.khung_danh_sach, orient="horizontal", command=self.tree_ds.xview)
        self.tree_ds.configure(yscrollcommand=cuon_doc_ds.set, xscrollcommand=cuon_ngang_ds.set)

        self.tree_ds.grid(row=0, column=0, sticky="nsew")
        cuon_doc_ds.grid(row=0, column=1, sticky="ns")
        cuon_ngang_ds.grid(row=1, column=0, sticky="ew")
        self.khung_danh_sach.columnconfigure(0, weight=1)
        self.khung_danh_sach.rowconfigure(0, weight=1)

        # 3. Ngăn kéo Nhật ký hoạt động nằm ở BÊN PHẢI (Right-side Panel)
        self.drawer_hoat_dong = ctk.CTkFrame(
            self.khu_vuc_chinh, width=320, fg_color="white", corner_radius=0,
            border_width=1, border_color="#d2d1df"
        )
        self.drawer_hoat_dong.pack_propagate(False)

        dau_hd = tk.Frame(self.drawer_hoat_dong, bg="#ffffff", padx=12, pady=10)
        dau_hd.pack(fill="x")
        tk.Label(
            dau_hd, text="Nhật ký hoạt động", bg="#ffffff",
            fg="#1e1b33", font=theme.FONT_DAM, anchor="w"
        ).pack(side="left")

        btn_dong_hd = ctk.CTkButton(
            dau_hd, text="✕", command=self._dong_drawer_hoat_dong,
            width=22, height=22, corner_radius=0,
            fg_color="#f1f5f9", hover_color="#fee2e2",
            border_width=0, text_color="#64748b", font=theme.FONT_NHO_DAM
        )
        btn_dong_hd.pack(side="right")

        tk.Frame(self.drawer_hoat_dong, bg="#e2e8f0", height=1).pack(fill="x")

        self.khung_ds_hd = tk.Frame(self.drawer_hoat_dong, bg="#ffffff")
        self.khung_ds_hd.pack(fill="both", expand=True)

        self.canvas_hd = tk.Canvas(self.khung_ds_hd, bg="#ffffff", highlightthickness=0)
        self.cuon_hd = ttk.Scrollbar(self.khung_ds_hd, orient="vertical", command=self.canvas_hd.yview)
        self.canvas_hd.configure(yscrollcommand=self.cuon_hd.set)

        self.noi_dung_hd = tk.Frame(self.canvas_hd, bg="#ffffff")
        self._cua_so_hd = self.canvas_hd.create_window((0, 0), window=self.noi_dung_hd, anchor="nw")

        self.canvas_hd.pack(side="left", fill="both", expand=True)
        self.cuon_hd.pack(side="right", fill="y")
        self.noi_dung_hd.bind("<Configure>", lambda _e: self.canvas_hd.configure(scrollregion=self.canvas_hd.bbox("all")))
        self.canvas_hd.bind("<Configure>", lambda e: self.canvas_hd.itemconfigure(self._cua_so_hd, width=e.width))

    def _dong_bo_kich_thuoc_kanban(self, chieu_rong=None, chieu_cao=None):
        """Đồng bộ chiều rộng các cột phủ đều 2 bên Canvas và kích hoạt cuộn ngang khi hẹp."""
        if getattr(self, "che_do_xem", "Bảng Kanban") != "Bảng Kanban":
            if self.thanh_cuon_ngang.winfo_ismapped():
                self.thanh_cuon_ngang.pack_forget()
            return
        cw = chieu_rong or self.canvas_kanban.winfo_width()
        ch = chieu_cao or self.canvas_kanban.winfo_height()
        if cw <= 1:
            cw = self.winfo_width()
        if ch <= 1:
            ch = self.winfo_height()

        so_cot = max(len(self.cot_widgets), 1)
        min_w = so_cot * 260
        rong = max(cw, min_w)
        cao = max(ch, 100)

        self.canvas_kanban.itemconfigure(self._cua_so_kanban, width=rong, height=cao)
        self.canvas_kanban.configure(scrollregion=(0, 0, rong, cao))

        can_cuon = min_w > cw and cw > 100
        if can_cuon and not self.thanh_cuon_ngang.winfo_ismapped():
            self.thanh_cuon_ngang.pack(side="bottom", fill="x")
        elif not can_cuon and self.thanh_cuon_ngang.winfo_ismapped():
            self.thanh_cuon_ngang.pack_forget()

    def _cap_nhat_vung_cuon_ngang(self, _event=None):
        self._dong_bo_kich_thuoc_kanban()

    def _khi_canvas_doi_co(self, event):
        self._dong_bo_kich_thuoc_kanban(event.width, event.height)

    def chuyen_che_do(self, che_do):
        """Chuyển đổi hiển thị giữa 'Bảng Kanban' và 'Danh sách'."""
        self.che_do_xem = che_do
        if che_do == "Bảng Kanban":
            self.khung_danh_sach.pack_forget()
            self.canvas_kanban.pack(fill="both", expand=True)
            self._cap_nhat_vung_cuon_ngang()
        else:
            self.canvas_kanban.pack_forget()
            if self.thanh_cuon_ngang.winfo_ismapped():
                self.thanh_cuon_ngang.pack_forget()
            self.khung_danh_sach.pack(fill="both", expand=True)

    def bat_tat_hoat_dong(self):
        """Bật hoặc tắt ngăn kéo hoạt động ở bên phải màn hình."""
        if self.drawer_hoat_dong.winfo_ismapped():
            self.drawer_hoat_dong.grid_forget()
            return False
        else:
            self.drawer_hoat_dong.grid(row=0, column=1, sticky="nsew", padx=(10, 0))
            return True

    def _dong_drawer_hoat_dong(self):
        self.drawer_hoat_dong.grid_forget()
        if self.khi_dong_hoat_dong:
            self.khi_dong_hoat_dong()

    def cap_nhat_kpi(self, tong, dang_lam, xong, khan):
        """Cập nhật số liệu trên 4 thẻ KPI."""
        self.lbl_kpis["tong"].configure(text=f"{tong} việc")
        self.lbl_kpis["dang_lam"].configure(text=f"{dang_lam} việc")
        self.lbl_kpis["xong"].configure(text=f"{xong} việc")
        self.lbl_kpis["khan"].configure(text=f"{khan} việc")

    def dung_cac_cot(self, danh_sach_ten_cot, ten_nguoi_map):
        """Tạo lại khung các cột trạng thái Kanban theo dạng grid căn đều 2 bên."""
        for c in self.khung_cac_cot.winfo_children():
            c.destroy()
        self.cot_widgets.clear()

        so_cot = len(danh_sach_ten_cot)
        self.khung_cac_cot.rowconfigure(0, weight=1)
        for idx in range(so_cot):
            self.khung_cac_cot.columnconfigure(idx, weight=1, uniform="cot_kanban")

        for idx, ten_cot in enumerate(danh_sach_ten_cot):
            w_cot = ColumnWidget(
                self.khung_cac_cot,
                ten_cot=ten_cot,
                ten_nguoi_map=ten_nguoi_map,
                khi_chon=self.khi_chon_task,
                khi_mo=self.khi_mo_task,
                khi_menu=self.khi_menu_task,
                khi_keo=self.khi_keo_task,
                khi_tha=self.khi_tha_task,
                khi_them_nhanh=self.khi_them_nhanh,
                khi_chuyen_nhanh=self.khi_chuyen_nhanh
            )
            w_cot.grid(row=0, column=idx, sticky="nsew", padx=4)
            self.cot_widgets[ten_cot] = w_cot

        self._dong_bo_kich_thuoc_kanban()

    def cap_nhat_hoat_dong(self, ds_nhat_ky):
        """Vẽ danh sách lịch sử thao tác vào ngăn kéo bên phải."""
        for c in self.noi_dung_hd.winfo_children():
            c.destroy()

        if not ds_nhat_ky:
            tk.Label(
                self.noi_dung_hd, text="Chưa có hoạt động nào",
                bg="#ffffff", fg="#94a3b8", font=theme.FONT_NHO, pady=20
            ).pack()
            return

        for nk in ds_nhat_ky[:30]:
            tg = nk.get("thoi_gian", "") if isinstance(nk, dict) else getattr(nk, "thoi_gian", "")
            nguoi = (nk.get("ten_dang_nhap", "") or nk.get("nguoi_thuc_hien", "")) if isinstance(nk, dict) else (getattr(nk, "ten_dang_nhap", "") or getattr(nk, "nguoi_thuc_hien", ""))
            ma = nk.get("ma_cong_viec", "") if isinstance(nk, dict) else getattr(nk, "ma_cong_viec", "")
            cu = nk.get("trang_thai_cu", "") if isinstance(nk, dict) else getattr(nk, "trang_thai_cu", "")
            moi = nk.get("trang_thai_moi", "") if isinstance(nk, dict) else getattr(nk, "trang_thai_moi", "")

            the_hd = tk.Frame(self.noi_dung_hd, bg="#f8fafc", padx=8, pady=6,
                              highlightthickness=1, highlightbackground="#e2e8f0")
            the_hd.pack(fill="x", padx=10, pady=4)

            tk.Label(the_hd, text=f"{tg} • {nguoi}",
                     bg="#f8fafc", fg="#64748b", font=theme.FONT_NHO, anchor="w").pack(fill="x")

            chi_tiet = f"Chuyển {ma}: {cu} → {moi}"
            tk.Label(the_hd, text=chi_tiet, bg="#f8fafc", fg="#0f172a",
                     font=theme.FONT_NHO_DAM, anchor="w", wraplength=270, justify="left").pack(fill="x", pady=(2, 0))
