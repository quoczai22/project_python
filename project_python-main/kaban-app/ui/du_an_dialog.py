"""Hộp thoại quản lý dự án: tạo dự án mới, quản lý thành viên dự án."""
import re
import tkinter as tk
from tkinter import ttk, messagebox

from config import TRANG_THAI_HOP_LE
from exceptions import KanbanException
from ui import theme
from ui.tien_ich import can_giua

TEN_VAI_TRO = {"quan_tri": "Quản trị viên", "thanh_vien": "Thành viên"}


def lay_danh_sach_nguoi_dung(ql):
    """Danh sách tài khoản trong hệ thống.
    Dùng hàm của facade nếu Quốc đã thêm, chưa có thì lấy qua bộ lưu trữ."""
    ham = getattr(ql, "lay_danh_sach_nguoi_dung", None)
    if ham:
        return ham()
    return ql.bo_luu_tru.doc_danh_sach_thanh_vien()


# ====================================================================== TẠO DỰ ÁN
class TaoDuAnDialog(tk.Toplevel):
    """Tạo dự án mới. Tạo xong gọi khi_xong(du_an_moi)."""

    def __init__(self, master, ql, khi_xong=None):
        super().__init__(master)
        self.ql = ql
        self.khi_xong = khi_xong

        self.title("Tạo dự án mới")
        self.configure(bg=theme.MAU_NEN)
        self.resizable(False, False)
        self.transient(master)

        self.var_ma = tk.StringVar(value=self._sinh_ma())
        self.var_ten = tk.StringVar()

        khung = ttk.Frame(self, padding=16)
        khung.pack(fill="both", expand=True)
        khung.columnconfigure(1, weight=1)

        ttk.Label(khung, text="Mã dự án *").grid(row=0, column=0, sticky="w", pady=5, padx=(0, 12))
        ttk.Entry(khung, textvariable=self.var_ma, width=32).grid(row=0, column=1, sticky="ew", pady=5)
        ttk.Label(khung, text="Định dạng DA-xxx (ví dụ DA-003)",
                  foreground=theme.MAU_CHU_PHU, font=theme.FONT_NHO
                  ).grid(row=1, column=1, sticky="w")

        ttk.Label(khung, text="Tên dự án *").grid(row=2, column=0, sticky="w", pady=5, padx=(0, 12))
        self.ent_ten = ttk.Entry(khung, textvariable=self.var_ten)
        self.ent_ten.grid(row=2, column=1, sticky="ew", pady=5)

        ttk.Label(khung, text="Các cột").grid(row=3, column=0, sticky="w", pady=5, padx=(0, 12))
        ttk.Label(khung, text="  →  ".join(TRANG_THAI_HOP_LE),
                  foreground=theme.MAU_CHU_PHU).grid(row=3, column=1, sticky="w")

        hang_nut = ttk.Frame(khung)
        hang_nut.grid(row=4, column=0, columnspan=2, sticky="e", pady=(14, 0))
        ttk.Button(hang_nut, text="Hủy", command=self.destroy).pack(side="right", padx=(8, 0))
        ttk.Button(hang_nut, text="Tạo dự án", style="Chinh.TButton",
                   command=self.luu).pack(side="right")

        self.ent_ten.bind("<Return>", lambda e: self.luu())
        self.bind("<Escape>", lambda e: self.destroy())
        can_giua(self)
        self.ent_ten.focus_set()
        self.wait_visibility()
        self.grab_set()

    def _sinh_ma(self):
        """Gợi ý mã DA-xxx tiếp theo."""
        so = []
        for d in self.ql.lay_danh_sach_du_an():
            m = re.fullmatch(r"DA-(\d+)", d.ma_du_an)
            if m:
                so.append(int(m.group(1)))
        return f"DA-{(max(so) + 1 if so else 1):03d}"

    def luu(self):
        ma = self.var_ma.get().strip().upper()
        ten = self.var_ten.get().strip()
        # Regex kiểm tra mã định danh ngay ở UI (backend cũng kiểm tra lại)
        if not re.fullmatch(r"DA-\d{3,}", ma):
            messagebox.showwarning("Mã không hợp lệ",
                                   "Mã dự án phải có dạng DA-xxx, ví dụ DA-003.", parent=self)
            return
        if not ten:
            messagebox.showwarning("Thiếu thông tin", "Tên dự án không được để trống.", parent=self)
            return
        try:
            du_an = self.ql.tao_du_an(ma, ten)
        except KanbanException as loi:       # ví dụ trùng mã, lỗi lưu file
            messagebox.showerror("Không tạo được dự án", loi.thong_diep, parent=self)
            return
        self.destroy()
        if self.khi_xong:
            self.khi_xong(du_an)


# ====================================================================== THÀNH VIÊN DỰ ÁN
class ThanhVienDuAnDialog(tk.Toplevel):
    """Xem / thêm / xóa thành viên của một dự án. Mỗi lần thay đổi gọi khi_xong()."""

    def __init__(self, master, ql, du_an, khi_xong=None):
        super().__init__(master)
        self.ql = ql
        self.du_an = du_an
        self.khi_xong = khi_xong
        self.nguoi_dung = {nd.ten_dang_nhap: nd for nd in lay_danh_sach_nguoi_dung(ql)}

        self.title(f"Thành viên - {du_an.ma_du_an}")
        self.configure(bg=theme.MAU_NEN)
        self.transient(master)
        self.var_them = tk.StringVar()

        self._dung_giao_dien()
        self._nap()
        self.bind("<Escape>", lambda e: self.destroy())
        can_giua(self)
        self.wait_visibility()
        self.grab_set()

    def _dung_giao_dien(self):
        khung = ttk.Frame(self, padding=16)
        khung.pack(fill="both", expand=True)

        ttk.Label(khung, text=f"{self.du_an.ma_du_an} - {self.du_an.ten_du_an}",
                  font=theme.FONT_DAM).pack(anchor="w")

        # Bảng thành viên (Treeview + Scrollbar, dùng grid trong khung riêng)
        bang = ttk.Frame(khung)
        bang.pack(fill="both", expand=True, pady=(8, 8))
        bang.columnconfigure(0, weight=1)
        bang.rowconfigure(0, weight=1)

        cac_cot = (("ten", "Tên đăng nhập", 120, "w"),
                   ("ho_ten", "Họ và tên", 200, "w"),
                   ("vai_tro", "Vai trò", 110, "center"),
                   ("so_viec", "Số việc", 70, "center"))
        self.tree = ttk.Treeview(bang, columns=[c[0] for c in cac_cot],
                                 show="headings", height=8, selectmode="browse")
        for khoa, tieu_de, rong, can in cac_cot:
            self.tree.heading(khoa, text=tieu_de)
            self.tree.column(khoa, width=rong, anchor=can)
        thanh = ttk.Scrollbar(bang, orient="vertical", command=self.tree.yview)
        self.tree.configure(yscrollcommand=thanh.set)
        self.tree.grid(row=0, column=0, sticky="nsew")
        thanh.grid(row=0, column=1, sticky="ns")

        # Hàng thêm thành viên
        hang_them = ttk.Frame(khung)
        hang_them.pack(fill="x")
        ttk.Label(hang_them, text="Thêm thành viên:").pack(side="left")
        self.cbb_them = ttk.Combobox(hang_them, textvariable=self.var_them,
                                     state="readonly", width=28)
        self.cbb_them.pack(side="left", padx=8)
        ttk.Button(hang_them, text="Thêm", style="Chinh.TButton",
                   command=self.them).pack(side="left")

        hang_nut = ttk.Frame(khung)
        hang_nut.pack(fill="x", pady=(12, 0))
        ttk.Button(hang_nut, text="Xóa thành viên đã chọn", command=self.xoa).pack(side="left")
        ttk.Button(hang_nut, text="Đóng", command=self.destroy).pack(side="right")

    # ------------------------------------------------------------ dữ liệu
    def _so_viec(self, ten):
        """Số công việc người này đang phụ trách trong dự án."""
        return sum(1 for cv in self.du_an.cong_viec if cv.nguoi_phu_trach == ten)

    def _nap(self):
        self.tree.delete(*self.tree.get_children())
        for ten in self.du_an.thanh_vien_tham_gia:
            nd = self.nguoi_dung.get(ten)
            ho_ten = nd.ho_ten if nd else "(không còn tài khoản)"
            vai_tro = TEN_VAI_TRO.get(nd.vai_tro, nd.vai_tro) if nd else ""
            self.tree.insert("", "end", iid=ten,
                             values=(ten, ho_ten, vai_tro, self._so_viec(ten)))

        # Quản trị viên đã có toàn quyền mọi dự án nên không đưa vào danh sách để thêm
        chua_co = [ten for ten, nd in self.nguoi_dung.items()
                   if ten not in self.du_an.thanh_vien_tham_gia and nd.vai_tro != "quan_tri"]
        self.cbb_them["values"] = chua_co
        self.var_them.set(chua_co[0] if chua_co else "")

    def _bao_doi(self):
        if self.khi_xong:
            self.khi_xong()

    # ------------------------------------------------------------ thao tác
    def them(self):
        ten = self.var_them.get()
        if not ten:
            messagebox.showinfo("Không còn ai để thêm",
                                "Tất cả tài khoản đã là thành viên của dự án này.", parent=self)
            return
        try:
            self.ql.them_thanh_vien_du_an(self.du_an, ten)
        except KanbanException as loi:
            messagebox.showerror("Không thêm được", loi.thong_diep, parent=self)
            return
        self._nap()
        self._bao_doi()

    def xoa(self):
        chon = self.tree.selection()
        if not chon:
            messagebox.showinfo("Chưa chọn", "Hãy chọn một thành viên trong bảng.", parent=self)
            return
        ten = chon[0]

        # Ràng buộc dữ liệu: không xóa người đang giữ việc trong dự án
        so_viec = self._so_viec(ten)
        if so_viec > 0:
            messagebox.showwarning(
                "Không thể xóa",
                f"'{ten}' đang phụ trách {so_viec} công việc trong dự án này.\n"
                "Hãy giao các việc đó cho người khác trước khi xóa.", parent=self)
            return
        if not messagebox.askyesno(
                "Xác nhận xóa",
                f"Xóa '{ten}' khỏi dự án {self.du_an.ma_du_an}?\n"
                "Người này sẽ không còn nhìn thấy dự án.", icon="warning", parent=self):
            return
        try:
            self.ql.xoa_thanh_vien_du_an(self.du_an, ten)
        except KanbanException as loi:
            messagebox.showerror("Không xóa được", loi.thong_diep, parent=self)
            return
        self._nap()
        self._bao_doi()