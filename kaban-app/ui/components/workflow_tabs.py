"""WorkflowTabs: Hai tab trực tiếp 'Chờ duyệt' và 'Đã hủy' ngay trên không gian làm việc."""
import tkinter as tk
from tkinter import ttk, messagebox, simpledialog

from ui.styles import theme


class _BangQuyTrinhBase(tk.Frame):
    """Khung cơ sở gồm thanh nút thao tác phía trên và bảng Treeview có thanh cuộn."""

    def __init__(self, master, cac_cot, cac_nut):
        super().__init__(master, bg="white", highlightthickness=1, highlightbackground="#e2e8f0")
        self.ql = self.du_an = self.khi_xong = None

        thanh = tk.Frame(self, bg="#f8fafc", padx=12, pady=8)
        thanh.pack(fill="x")
        for loai, nhan, fn, rong in cac_nut:
            if loai == "chinh":
                btn = theme.tao_nut_chinh(thanh, text=nhan, command=fn, width=rong, height=30)
            elif loai == "nguy_hiem":
                btn = theme.tao_nut_nguy_hiem(thanh, text=nhan, command=fn, width=rong, height=30)
            else:
                btn = theme.tao_nut_phu(thanh, text=nhan, command=fn, width=rong, height=30)
            btn.pack(side="left", padx=(0, 6))

        self.lbl_dem = tk.Label(thanh, text="0 mục", bg="#f8fafc", fg="#64748b", font=theme.FONT_NHO_DAM)
        self.lbl_dem.pack(side="right")

        tk.Frame(self, bg="#e2e8f0", height=1).pack(fill="x")

        bang = tk.Frame(self, bg="white")
        bang.pack(fill="both", expand=True)
        bang.columnconfigure(0, weight=1)
        bang.rowconfigure(0, weight=1)

        self.tree = ttk.Treeview(bang, columns=[c[0] for c in cac_cot], show="headings", selectmode="browse")
        for k, t, w, a in cac_cot:
            self.tree.heading(k, text=t)
            self.tree.column(k, width=w, anchor=a, stretch=(k in ("tieu_de", "chi_tiet", "ly_do")))

        cuon_doc = ttk.Scrollbar(bang, orient="vertical", command=self.tree.yview)
        cuon_ngang = ttk.Scrollbar(bang, orient="horizontal", command=self.tree.xview)
        self.tree.configure(yscrollcommand=cuon_doc.set, xscrollcommand=cuon_ngang.set)
        self.tree.grid(row=0, column=0, sticky="nsew")
        cuon_doc.grid(row=0, column=1, sticky="ns")
        cuon_ngang.grid(row=1, column=0, sticky="ew")

    def _thuc_thi(self, fn):
        chon = self.tree.selection()
        if not chon:
            messagebox.showinfo("Chưa chọn", "Hãy chọn một công việc trong danh sách.", parent=self.winfo_toplevel())
            return
        if not self.ql or not self.du_an:
            return
        try:
            fn(self.du_an, chon[0])
        except Exception as err:
            messagebox.showerror("Không thực hiện được", getattr(err, "thong_diep", str(err)), parent=self.winfo_toplevel())
            return
        if self.khi_xong:
            self.khi_xong()


class TabChoDuyetComponent(_BangQuyTrinhBase):
    """Tab Chờ duyệt: hiển thị việc chờ duyệt/từ chối và yêu cầu mở lại, gia hạn."""

    def __init__(self, master):
        cac_cot = (
            ("ma", "Mã", 75, "center"),
            ("tieu_de", "Tiêu đề", 220, "w"),
            ("nguoi", "Phụ trách", 135, "w"),
            ("trang_thai", "Trạng thái", 100, "center"),
            ("loai", "Loại duyệt", 120, "center"),
            ("chi_tiet", "Chi tiết / Lý do", 280, "w"),
        )
        cac_nut = (
            ("chinh", "Duyệt việc", lambda: self._thuc_thi(self.ql.duyet_cong_viec), 88),
            ("nguy_hiem", "Từ chối việc", lambda: self._thuc_thi(lambda d, m: self.ql.duyet_cong_viec(d, m, False)), 96),
            ("phu", "Gửi lại", lambda: self._thuc_thi(self.ql.gui_lai_cong_viec), 70),
            ("chinh", "Duyệt HT", lambda: self._thuc_thi(self.ql.duyet_hoan_thanh), 88),
            ("nguy_hiem", "Từ chối HT", self._tu_choi_hoan_thanh, 92),
            ("chinh", "Duyệt mở lại", lambda: self._thuc_thi(self.ql.duyet_mo_lai), 102),
            ("phu", "Từ chối mở lại", lambda: self._thuc_thi(lambda d, m: self.ql.duyet_mo_lai(d, m, False)), 108),
            ("chinh", "Duyệt gia hạn", lambda: self._thuc_thi(self.ql.duyet_gia_han), 106),
            ("phu", "Từ chối gia hạn", lambda: self._thuc_thi(lambda d, m: self.ql.duyet_gia_han(d, m, False)), 112),
        )
        super().__init__(master, cac_cot, cac_nut)

    def _tu_choi_hoan_thanh(self):
        chon = self.tree.selection()
        if not chon:
            messagebox.showinfo("Chưa chọn", "Hãy chọn một công việc trong danh sách.", parent=self.winfo_toplevel())
            return
        ly_do = simpledialog.askstring("Từ chối hoàn thành", "Nhập lý do từ chối:", parent=self.winfo_toplevel())
        if ly_do is None:
            return
        self._thuc_thi(lambda d, m: self.ql.duyet_hoan_thanh(d, m, False, ly_do))

    def cap_nhat(self, ql, du_an, ten_nguoi_map, khi_xong):
        self.ql, self.du_an, self.khi_xong = ql, du_an, khi_xong
        self.tree.delete(*self.tree.get_children())
        if not du_an:
            self.lbl_dem.configure(text="0 mục")
            return
        dem = 0
        for cv in du_an.cong_viec:
            if cv.trang_thai == "Đã hủy":
                continue
            co_duyet = getattr(cv, "trang_thai_duyet", "da_duyet") in ("cho_duyet", "tu_choi")
            cho_ht = cv.trang_thai == "Kiểm tra" and getattr(cv, "trang_thai_duyet", "da_duyet") == "da_duyet"
            if not (co_duyet or cho_ht or cv.yeu_cau_mo_lai or cv.yeu_cau_gia_han):
                continue
            loai, chi_tiet = [], []
            if cv.trang_thai_duyet == "cho_duyet":
                loai.append("Chờ duyệt tạo")
                chi_tiet.append(f"Tạo bởi {ten_nguoi_map.get(cv.nguoi_tao, cv.nguoi_tao)}")
            elif cv.trang_thai_duyet == "tu_choi":
                loai.append("Bị từ chối")
                chi_tiet.append("Cần người tạo gửi lại")
            if cho_ht:
                loai.append("Chờ duyệt HT")
                chi_tiet.append("Đang ở cột Kiểm tra, chờ duyệt hoàn thành")
            if cv.yeu_cau_mo_lai:
                yc = cv.yeu_cau_mo_lai
                loai.append("Xin mở lại")
                chi_tiet.append(f"Mở lại ({yc.get('nguoi', '')}): {yc.get('ly_do', '')}")
            if cv.yeu_cau_gia_han:
                yc = cv.yeu_cau_gia_han
                loai.append("Xin gia hạn")
                chi_tiet.append(f"Gia hạn -> {yc.get('han_moi', '')} ({yc.get('nguoi', '')}): {yc.get('ly_do', '')}")
            ten_tv = ten_nguoi_map.get(cv.nguoi_phu_trach, cv.nguoi_phu_trach)
            self.tree.insert("", "end", iid=cv.ma_cong_viec,
                             values=(cv.ma_cong_viec, cv.tieu_de, ten_tv, cv.trang_thai,
                                     ", ".join(loai), " | ".join(chi_tiet)))
            dem += 1
        self.lbl_dem.configure(text=f"{dem} yêu cầu")


class TabDaHuyComponent(_BangQuyTrinhBase):
    """Tab Đã hủy: danh sách công việc xóa mềm để Admin/Leader khôi phục."""

    def __init__(self, master):
        cac_cot = (
            ("ma", "Mã", 75, "center"),
            ("tieu_de", "Tiêu đề", 230, "w"),
            ("nguoi", "Phụ trách", 135, "w"),
            ("trang_thai_cu", "Cột trước hủy", 110, "center"),
            ("nguoi_huy", "Người hủy", 115, "w"),
            ("ly_do", "Lý do & Thời gian hủy", 280, "w"),
        )
        cac_nut = (
            ("chinh", "Khôi phục công việc", lambda: self._thuc_thi(self.ql.khoi_phuc_cong_viec), 165),
        )
        super().__init__(master, cac_cot, cac_nut)

    def cap_nhat(self, ql, du_an, ten_nguoi_map, khi_xong):
        self.ql, self.du_an, self.khi_xong = ql, du_an, khi_xong
        self.tree.delete(*self.tree.get_children())
        if not du_an:
            self.lbl_dem.configure(text="0 việc đã hủy")
            return
        dem = 0
        for cv in du_an.cong_viec:
            if cv.trang_thai != "Đã hủy":
                continue
            ten_tv = ten_nguoi_map.get(cv.nguoi_phu_trach, cv.nguoi_phu_trach)
            nguoi_huy = ten_nguoi_map.get(cv.nguoi_huy, cv.nguoi_huy)
            thoi_gian = (cv.thoi_gian_huy or "")[:19].replace("T", " ")
            mo_ta = f"{cv.ly_do_huy} ({thoi_gian})" if thoi_gian else cv.ly_do_huy
            self.tree.insert("", "end", iid=cv.ma_cong_viec,
                             values=(cv.ma_cong_viec, cv.tieu_de, ten_tv,
                                     cv.trang_thai_truoc_huy or "Cần làm", nguoi_huy, mo_ta))
            dem += 1
        self.lbl_dem.configure(text=f"{dem} việc đã hủy")
