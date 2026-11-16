"""StatsView: Cửa sổ thống kê tiến độ, KPI tổng quan, biểu đồ và cảnh báo đa hình OOP."""
import math
import tkinter as tk
from tkinter import ttk
import customtkinter as ctk

from ui.styles import theme
from utils.helpers import can_giua


class StatsView(tk.Toplevel):
    """
    Màn hình thống kê dự án:
    - 4 thẻ KPI Dashboard
    - Thanh tiến độ tổng quan
    - Biểu đồ phân bổ trạng thái trực quan vẽ bằng Canvas
    - Bảng cảnh báo đa hình OOP & Nhật ký chuyển trạng thái
    """

    def __init__(self, master, du_an, ql=None):
        super().__init__(master)
        self.du_an = du_an
        self.ql = ql
        self.so_lieu = {}

        self.title("Thống kê dự án")
        self.configure(bg=theme.MAU_NEN)
        self.minsize(820, 660)

        self.var_chua_xong = tk.BooleanVar(value=True)
        self.che_do_bang = "Cảnh báo thời hạn"

        self._dung_giao_dien()
        can_giua(self, 940, 740)
        self.cap_nhat()

    def _dung_giao_dien(self):
        theme.tao_header_figma(
            self,
            tieu_de="Biểu đồ tiến độ, cảnh báo & nhật ký",
            badge_text="TK",
            cao=74
        )

        # 1. KPI tổng quan
        hang_kpi = tk.Frame(self, bg=theme.MAU_NEN)
        hang_kpi.pack(fill="x", padx=14, pady=(10, 6))
        for i in range(4):
            hang_kpi.columnconfigure(i, weight=1, uniform="kpi")

        self.lbl_kpi = {}
        self.lbl_kpi_phu = {}
        cau_hinh_kpi = (
            ("tong", "Tổng công việc", theme.MAU_CHU),
            ("hoan_thanh", "Hoàn thành", theme.MAU_HOAN_THANH),
            ("dang_lam", "Đang thực hiện", theme.MAU_CHINH),
            ("canh_bao", "Quá hạn / Khẩn", theme.MAU_LOI),
        )
        for cot_idx, (khoa, tieu_de, mau) in enumerate(cau_hinh_kpi):
            pad_phai = (0, 8) if cot_idx < 3 else (0, 0)
            the = ctk.CTkFrame(
                hang_kpi, fg_color=theme.MAU_THE, corner_radius=0,
                border_width=1, border_color=theme.MAU_VIEN
            )
            the.grid(row=0, column=cot_idx, sticky="ew", padx=pad_phai)

            dau_the = tk.Frame(the, bg=theme.MAU_THE)
            dau_the.pack(fill="x", padx=14, pady=(8, 0))
            tk.Label(
                dau_the, text=tieu_de, bg=theme.MAU_THE, fg=theme.MAU_CHU_PHU,
                font=theme.FONT_CHUAN, anchor="w"
            ).pack(side="left")
            lbl_phu = ctk.CTkLabel(
                dau_the, text="", corner_radius=0, height=20, padx=7,
                fg_color="#f1f5f9", text_color=mau,
                bg_color=theme.MAU_THE, font=theme.FONT_NHO_DAM
            )
            lbl_phu.pack(side="right")
            self.lbl_kpi_phu[khoa] = lbl_phu

            lbl_gia_tri = tk.Label(
                the, text="0", bg=theme.MAU_THE, fg=mau,
                font=theme.FONT_KPI, anchor="w"
            )
            lbl_gia_tri.pack(fill="x", padx=14, pady=(0, 8))
            self.lbl_kpi[khoa] = lbl_gia_tri

        # 2. Thanh tiến độ
        khung_td = ctk.CTkFrame(
            self, fg_color=theme.MAU_THE, corner_radius=0,
            border_width=1, border_color=theme.MAU_VIEN
        )
        khung_td.pack(fill="x", padx=14, pady=(0, 6))

        self.lbl_tien_do = tk.Label(
            khung_td, bg=theme.MAU_THE, fg=theme.MAU_CHU, font=theme.FONT_DAM, anchor="w"
        )
        self.lbl_tien_do.pack(fill="x", padx=16, pady=(8, 4))

        self.thanh_tien_do = ctk.CTkProgressBar(
            khung_td, height=11, corner_radius=0,
            fg_color=theme.MAU_NEN, progress_color=theme.MAU_CHINH
        )
        self.thanh_tien_do.pack(fill="x", padx=16, pady=(0, 10))
        self.thanh_tien_do.set(0)

        # 3. Biểu đồ cột
        khung_bd = ctk.CTkFrame(
            self, fg_color=theme.MAU_THE, corner_radius=0,
            border_width=1, border_color=theme.MAU_VIEN
        )
        khung_bd.pack(fill="both", expand=True, padx=14, pady=(0, 6))

        self.canvas = tk.Canvas(khung_bd, bg=theme.MAU_THE, height=175, highlightthickness=0)
        self.canvas.pack(fill="both", expand=True, padx=8, pady=6)
        self.canvas.bind("<Configure>", self.ve_bieu_do)

        # 4. Bảng cảnh báo & nhật ký
        khung_duoi = ctk.CTkFrame(
            self, fg_color=theme.MAU_THE, corner_radius=0,
            border_width=1, border_color=theme.MAU_VIEN
        )
        khung_duoi.pack(fill="both", expand=True, padx=14, pady=(0, 12))

        duoi = tk.Frame(khung_duoi, bg=theme.MAU_THE, padx=14, pady=8)
        duoi.pack(fill="both", expand=True)
        duoi.columnconfigure(0, weight=1)
        duoi.rowconfigure(1, weight=1)

        thanh_tab = tk.Frame(duoi, bg=theme.MAU_THE)
        thanh_tab.grid(row=0, column=0, columnspan=2, sticky="ew", pady=(0, 8))

        gia_tri_tab = ["Cảnh báo thời hạn"]
        if self.ql is not None:
            gia_tri_tab.append("Nhật ký chuyển trạng thái")

        self.seg_bang = ctk.CTkSegmentedButton(
            thanh_tab,
            values=gia_tri_tab,
            command=self._doi_bang,
            font=theme.FONT_NHO_DAM,
            fg_color=theme.MAU_COT,
            selected_color=theme.MAU_THE,
            selected_hover_color=theme.MAU_THE,
            unselected_color=theme.MAU_COT,
            unselected_hover_color="#d5dfe7",
            text_color=theme.MAU_CHU,
            border_width=3,
            height=32,
            corner_radius=0
        )
        self.seg_bang.pack(side="left")
        self.seg_bang.set("Cảnh báo thời hạn")

        self.chk_chua_xong = ctk.CTkCheckBox(
            thanh_tab, text="Chỉ hiện việc chưa hoàn thành",
            variable=self.var_chua_xong, command=self._nap_canh_bao,
            font=theme.FONT_NHO, text_color=theme.MAU_CHU_NHAN,
            fg_color=theme.MAU_CHINH, hover_color=theme.MAU_CHINH_DAM,
            border_color=theme.MAU_VIEN_THE, corner_radius=0,
            checkbox_width=18, checkbox_height=18
        )
        self.chk_chua_xong.pack(side="right")

        self.vung_tree = tk.Frame(duoi, bg=theme.MAU_THE)
        self.vung_tree.grid(row=1, column=0, columnspan=2, sticky="nsew")
        self.vung_tree.columnconfigure(0, weight=1)
        self.vung_tree.rowconfigure(0, weight=1)

        cac_cot_cb = (
            ("ma", "Mã", 80, "center"),
            ("tieu_de", "Tiêu đề", 260, "w"),
            ("loai", "Loại công việc", 140, "w"),
            ("canh_bao", "Cảnh báo (Đa hình OOP)", 320, "w"),
        )
        self.tree = ttk.Treeview(
            self.vung_tree, columns=[c[0] for c in cac_cot_cb],
            show="headings", height=4, selectmode="browse"
        )
        for khoa, tieu_de, rong, can in cac_cot_cb:
            self.tree.heading(khoa, text=tieu_de)
            self.tree.column(khoa, width=rong, anchor=can)
        self.tree.tag_configure("qua_han", foreground=theme.MAU_LOI)
        self.tree.tag_configure("khan", foreground=theme.MAU_CANH_BAO)

        self.thanh_cb = ttk.Scrollbar(self.vung_tree, orient="vertical", command=self.tree.yview)
        self.tree.configure(yscrollcommand=self.thanh_cb.set)

        cac_cot_nk = (
            ("thoi_gian", "Thời gian", 160, "center"),
            ("nguoi", "Người thực hiện", 130, "w"),
            ("ma", "Mã việc", 90, "center"),
            ("cu", "Trạng thái cũ", 160, "center"),
            ("moi", "Trạng thái mới", 160, "center"),
        )
        self.tree_nk = ttk.Treeview(
            self.vung_tree, columns=[c[0] for c in cac_cot_nk],
            show="headings", height=4, selectmode="browse"
        )
        for khoa, tieu_de, rong, can in cac_cot_nk:
            self.tree_nk.heading(khoa, text=tieu_de)
            self.tree_nk.column(khoa, width=rong, anchor=can)

        self.thanh_nk = ttk.Scrollbar(self.vung_tree, orient="vertical", command=self.tree_nk.yview)
        self.tree_nk.configure(yscrollcommand=self.thanh_nk.set)

        self._hien_thi_tree_hien_tai()

    def _doi_bang(self, ten_bang):
        self.che_do_bang = ten_bang
        self._hien_thi_tree_hien_tai()
        if ten_bang == "Cảnh báo thời hạn":
            self._nap_canh_bao()
        else:
            self._nap_nhat_ky()

    def _hien_thi_tree_hien_tai(self):
        self.tree.grid_forget()
        self.thanh_cb.grid_forget()
        self.tree_nk.grid_forget()
        self.thanh_nk.grid_forget()

        if self.che_do_bang == "Cảnh báo thời hạn":
            self.chk_chua_xong.pack(side="right")
            self.tree.grid(row=0, column=0, sticky="nsew")
            self.thanh_cb.grid(row=0, column=1, sticky="ns")
        else:
            self.chk_chua_xong.pack_forget()
            self.tree_nk.grid(row=0, column=0, sticky="nsew")
            self.thanh_nk.grid(row=0, column=1, sticky="ns")

    def dat_du_an(self, du_an):
        self.du_an = du_an
        self.cap_nhat()

    def cap_nhat(self):
        da = self.du_an
        self.so_lieu = {ten: 0 for ten in da.danh_sach_cot}
        for cv in da.cong_viec:
            if cv.trang_thai in self.so_lieu:
                self.so_lieu[cv.trang_thai] += 1

        tong = len(da.cong_viec)
        xong = self.so_lieu.get("Hoàn thành", 0)
        dang_lam = self.so_lieu.get("Đang làm", 0) + self.so_lieu.get("Kiểm tra", 0)
        canh_bao = sum(
            1 for cv in da.cong_viec
            if cv.can_chu_y()
        )

        ty_le = (xong / tong * 100) if tong > 0 else 0.0

        self.lbl_kpi["tong"].configure(text=str(tong))
        self.lbl_kpi_phu["tong"].configure(text=f"{len(da.danh_sach_cot)} cột")

        self.lbl_kpi["hoan_thanh"].configure(text=str(xong))
        self.lbl_kpi_phu["hoan_thanh"].configure(text=f"{ty_le:.0f}%")

        self.lbl_kpi["dang_lam"].configure(text=str(dang_lam))
        tl_dl = (dang_lam / tong * 100) if tong > 0 else 0.0
        self.lbl_kpi_phu["dang_lam"].configure(text=f"{tl_dl:.0f}%")

        self.lbl_kpi["canh_bao"].configure(text=str(canh_bao))
        self.lbl_kpi_phu["canh_bao"].configure(text="Cần xử lý" if canh_bao > 0 else "Ổn định")

        self.lbl_tien_do.configure(text=f"Tiến độ tổng thể dự án: {ty_le:.1f}% ({xong}/{tong} công việc)")
        self.thanh_tien_do.set(min(max(ty_le / 100.0, 0.0), 1.0))

        self.ve_bieu_do()
        if self.che_do_bang == "Cảnh báo thời hạn":
            self._nap_canh_bao()
        else:
            self._nap_nhat_ky()

    def ve_bieu_do(self, _event=None):
        self.canvas.delete("all")
        w = self.canvas.winfo_width()
        h = self.canvas.winfo_height()
        if w < 100 or h < 80:
            return

        ds_cot = self.du_an.danh_sach_cot
        if not ds_cot:
            return

        gia_tri = [self.so_lieu.get(c, 0) for c in ds_cot]
        max_val = max(gia_tri) if gia_tri else 0
        tong_all = sum(gia_tri)
        gioi_han_y = max(max_val, 5)

        le_trai = 40
        le_phai = 20
        le_tren = 20
        le_duoi = 38
        w_ve = w - le_trai - le_phai
        h_ve = h - le_tren - le_duoi

        buoc_y = max(1, math.ceil(gioi_han_y / 4))
        for moc in range(0, gioi_han_y + 1, buoc_y):
            y = le_tren + h_ve - (moc / gioi_han_y * h_ve)
            self.canvas.create_line(le_trai, y, w - le_phai, y, fill="#e2e8f0", width=1)
            self.canvas.create_text(le_trai - 8, y, text=str(moc), anchor="e",
                                    fill=theme.MAU_CHU_PHU, font=theme.FONT_NHO)

        so_cot = len(ds_cot)
        khoang_moi_cot = w_ve / so_cot
        be_rong_cot = min(68, max(26, khoang_moi_cot * 0.48))

        for i, ten in enumerate(ds_cot):
            so = gia_tri[i]
            x_giua = le_trai + (i + 0.5) * khoang_moi_cot
            x0 = x_giua - be_rong_cot / 2
            x1 = x_giua + be_rong_cot / 2

            cao_cot = (so / gioi_han_y * h_ve) if gioi_han_y > 0 else 0
            y0 = le_tren + h_ve - cao_cot
            y1 = le_tren + h_ve

            mau = theme.MAU_CHINH if so > 0 else "#e2e8f0"
            self.canvas.create_rectangle(x0, y0, x1, y1, fill=mau, outline="")

            pt = f" ({so / tong_all * 100:.0f}%)" if (tong_all > 0 and so > 0) else ""
            self.canvas.create_text(x_giua, max(le_tren + 4, y0 - 10),
                                    text=f"{so}{pt}", fill=theme.MAU_CHU, font=theme.FONT_NHO_DAM)

            self.canvas.create_text(x_giua, h - le_duoi + 14,
                                    text=ten, fill=theme.MAU_CHU_PHU, font=theme.FONT_NHO)

    def _nap_canh_bao(self):
        self.tree.delete(*self.tree.get_children())
        chi_chua_xong = self.var_chua_xong.get()

        for cv in self.du_an.cong_viec:
            if chi_chua_xong and cv.is_hoan_thanh():
                continue

            thong_diep = cv.canh_bao()
            tag = ""
            if cv.da_qua_han() and not cv.is_hoan_thanh():
                tag = "qua_han"
            elif cv.muc_uu_tien == "Khẩn":
                tag = "khan"

            self.tree.insert(
                "", "end", iid=cv.ma_cong_viec,
                values=(cv.ma_cong_viec, cv.tieu_de, cv.lay_loai_cong_viec(), thong_diep),
                tags=(tag,) if tag else ()
            )

    def _nap_nhat_ky(self):
        self.tree_nk.delete(*self.tree_nk.get_children())
        if self.ql is None:
            return
        ds = self.ql.lay_nhat_ky()
        for i, nk in enumerate(ds[:100]):
            tg = nk.get("thoi_gian", "") if isinstance(nk, dict) else getattr(nk, "thoi_gian", "")
            nguoi = (nk.get("ten_dang_nhap", "") or nk.get("nguoi_thuc_hien", "")) if isinstance(nk, dict) else (getattr(nk, "ten_dang_nhap", "") or getattr(nk, "nguoi_thuc_hien", ""))
            ma = nk.get("ma_cong_viec", "") if isinstance(nk, dict) else getattr(nk, "ma_cong_viec", "")
            cu = (nk.get("trang_thai_cu", "") or "(mới)") if isinstance(nk, dict) else (getattr(nk, "trang_thai_cu", "") or "(mới)")
            moi = nk.get("trang_thai_moi", "") if isinstance(nk, dict) else getattr(nk, "trang_thai_moi", "")
            self.tree_nk.insert(
                "", "end", iid=f"nk_{i}",
                values=(tg, nguoi, ma, cu, moi)
            )


# Alias tương thích ngược
ThongKeWindow = StatsView
