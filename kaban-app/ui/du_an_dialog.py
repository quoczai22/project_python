"""Hộp thoại quản lý dự án: tạo dự án mới, quản lý thành viên dự án (Tkinter + CustomTkinter)."""
import re
import tkinter as tk
from tkinter import ttk, messagebox
import customtkinter as ctk

from config import TRANG_THAI_HOP_LE
from exceptions import KanbanException
from ui import theme
from ui.tien_ich import can_giua

TEN_VAI_TRO = {"quan_tri": "Quản trị viên", "thanh_vien": "Thành viên"}


def lay_danh_sach_nguoi_dung(ql):
    """Danh sách tài khoản trong hệ thống."""
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

        khung_ngoai = ctk.CTkFrame(
            self, fg_color=theme.MAU_THE, corner_radius=14,
            border_width=1, border_color=theme.MAU_VIEN
        )
        khung_ngoai.pack(fill="both", expand=True, padx=12, pady=12)

        theme.tao_header_figma(
            khung_ngoai,
            eyebrow="KANBAN / DỰ ÁN",
            tieu_de="KHỞI TẠO DỰ ÁN MỚI",
            badge_text="DA",
            cao=76
        )

        khung = tk.Frame(khung_ngoai, bg=theme.MAU_THE, padx=26, pady=18)
        khung.pack(fill="both", expand=True)

        tk.Label(khung, text="Mã dự án * (Định dạng DA-xxx)", bg=theme.MAU_THE,
                 fg=theme.MAU_CHU_NHAN, font=theme.FONT_DAM, anchor="w").pack(fill="x", pady=(0, 4))
        self.ent_ma = ctk.CTkEntry(
            khung, textvariable=self.var_ma, placeholder_text="DA-003",
            height=38, corner_radius=6, fg_color=theme.MAU_O_NHAP,
            border_color=theme.MAU_VIEN_THE, border_width=1,
            text_color=theme.MAU_CHU, font=theme.FONT_CHUAN
        )
        self.ent_ma.pack(fill="x", pady=(0, 12))

        tk.Label(khung, text="Tên dự án *", bg=theme.MAU_THE,
                 fg=theme.MAU_CHU_NHAN, font=theme.FONT_DAM, anchor="w").pack(fill="x", pady=(0, 4))
        self.ent_ten = ctk.CTkEntry(
            khung, textvariable=self.var_ten, placeholder_text="Nhập tên dự án...",
            height=38, corner_radius=6, fg_color=theme.MAU_O_NHAP,
            border_color=theme.MAU_VIEN_THE, border_width=1,
            text_color=theme.MAU_CHU, font=theme.FONT_CHUAN
        )
        self.ent_ten.pack(fill="x", pady=(0, 12))

        tk.Label(khung, text="Các cột trạng thái mặc định", bg=theme.MAU_THE,
                 fg=theme.MAU_CHU_NHAN, font=theme.FONT_DAM, anchor="w").pack(fill="x", pady=(0, 4))
        khung_cot = ctk.CTkFrame(khung, fg_color=theme.MAU_CHINH_NHAT, corner_radius=6)
        khung_cot.pack(fill="x", pady=(0, 14))
        tk.Label(khung_cot, text="   →   ".join(TRANG_THAI_HOP_LE),
                 bg=theme.MAU_CHINH_NHAT, fg=theme.MAU_CHINH,
                 font=theme.FONT_DAM, pady=8).pack()

        tk.Frame(khung, bg=theme.MAU_VIEN, height=1).pack(fill="x", pady=(4, 12))
        hang_nut = tk.Frame(khung, bg=theme.MAU_THE)
        hang_nut.pack(fill="x")

        ctk.CTkButton(
            hang_nut, text="Tạo dự án", command=self.luu,
            width=120, height=38, corner_radius=7,
            fg_color=theme.MAU_CHINH, hover_color=theme.MAU_CHINH_DAM,
            text_color="white", font=theme.FONT_DAM
        ).pack(side="right")

        ctk.CTkButton(
            hang_nut, text="Hủy", command=self.destroy,
            width=90, height=38, corner_radius=7,
            fg_color="white", hover_color=theme.MAU_NEN,
            border_width=1, border_color=theme.MAU_VIEN_THE,
            text_color=theme.MAU_CHU_NHAN, font=theme.FONT_DAM
        ).pack(side="right", padx=(0, 8))

        self.ent_ten.bind("<Return>", lambda e: self.luu())
        self.bind("<Escape>", lambda e: self.destroy())
        can_giua(self, 460, 390)
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
        if not re.fullmatch(r"DA-\d{3,}", ma):
            messagebox.showwarning("Mã không hợp lệ",
                                   "Mã dự án phải có dạng DA-xxx, ví dụ DA-003.", parent=self)
            return
        if not ten:
            messagebox.showwarning("Thiếu thông tin", "Tên dự án không được để trống.", parent=self)
            return
        try:
            du_an = self.ql.tao_du_an(ma, ten)
        except KanbanException as loi:
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
        can_giua(self, 620, 490)
        self.wait_visibility()
        self.grab_set()

    def _dung_giao_dien(self):
        khung_ngoai = ctk.CTkFrame(
            self, fg_color=theme.MAU_THE, corner_radius=14,
            border_width=1, border_color=theme.MAU_VIEN
        )
        khung_ngoai.pack(fill="both", expand=True, padx=12, pady=12)

        theme.tao_header_figma(
            khung_ngoai,
            eyebrow=f"DỰ ÁN {self.du_an.ma_du_an}",
            tieu_de=f"THÀNH VIÊN: {self.du_an.ten_du_an.upper()}",
            badge_text="TV",
            cao=76
        )

        khung = tk.Frame(khung_ngoai, bg=theme.MAU_THE, padx=24, pady=16)
        khung.pack(fill="both", expand=True)

        # Bảng thành viên (Treeview + Scrollbar)
        bang = tk.Frame(khung, bg=theme.MAU_THE)
        bang.pack(fill="both", expand=True, pady=(0, 12))
        bang.columnconfigure(0, weight=1)
        bang.rowconfigure(0, weight=1)

        cac_cot = (("ten", "Tên đăng nhập", 130, "w"),
                   ("ho_ten", "Họ và tên", 210, "w"),
                   ("vai_tro", "Vai trò", 120, "center"),
                   ("so_viec", "Số việc", 80, "center"))
        self.tree = ttk.Treeview(bang, columns=[c[0] for c in cac_cot],
                                 show="headings", height=7, selectmode="browse")
        for khoa, tieu_de, rong, can in cac_cot:
            self.tree.heading(khoa, text=tieu_de)
            self.tree.column(khoa, width=rong, anchor=can)
        thanh = ttk.Scrollbar(bang, orient="vertical", command=self.tree.yview)
        self.tree.configure(yscrollcommand=thanh.set)
        self.tree.grid(row=0, column=0, sticky="nsew")
        thanh.grid(row=0, column=1, sticky="ns")

        # Hàng thêm thành viên
        hang_them = tk.Frame(khung, bg=theme.MAU_THE)
        hang_them.pack(fill="x", pady=(4, 12))
        tk.Label(hang_them, text="Thêm thành viên:", bg=theme.MAU_THE,
                 fg=theme.MAU_CHU_NHAN, font=theme.FONT_DAM).pack(side="left")
        self.cbb_them = ctk.CTkComboBox(
            hang_them, variable=self.var_them, values=[],
            state="readonly", width=230, height=34, corner_radius=6,
            fg_color=theme.MAU_O_NHAP, border_color=theme.MAU_VIEN_THE, border_width=1,
            button_color=theme.MAU_VIEN_THE, button_hover_color=theme.MAU_CHINH_NHAT,
            text_color=theme.MAU_CHU, font=theme.FONT_CHUAN
        )
        self.cbb_them.pack(side="left", padx=10)
        ctk.CTkButton(
            hang_them, text="+ Thêm vào dự án", command=self.them,
            width=130, height=34, corner_radius=6,
            fg_color=theme.MAU_CHINH, hover_color=theme.MAU_CHINH_DAM,
            text_color="white", font=theme.FONT_DAM
        ).pack(side="left")

        tk.Frame(khung, bg=theme.MAU_VIEN, height=1).pack(fill="x", pady=(0, 10))
        hang_nut = tk.Frame(khung, bg=theme.MAU_THE)
        hang_nut.pack(fill="x")
        ctk.CTkButton(
            hang_nut, text="Xóa thành viên đã chọn", command=self.xoa,
            width=170, height=36, corner_radius=6,
            fg_color="white", hover_color="#fee2e2",
            border_width=1, border_color=theme.MAU_VIEN_THE,
            text_color=theme.MAU_LOI, font=theme.FONT_DAM
        ).pack(side="left")
        ctk.CTkButton(
            hang_nut, text="Đóng", command=self.destroy,
            width=90, height=36, corner_radius=6,
            fg_color="white", hover_color=theme.MAU_NEN,
            border_width=1, border_color=theme.MAU_VIEN_THE,
            text_color=theme.MAU_CHU_NHAN, font=theme.FONT_DAM
        ).pack(side="right")

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

        chua_co = [ten for ten, nd in self.nguoi_dung.items()
                   if ten not in self.du_an.thanh_vien_tham_gia and nd.vai_tro != "quan_tri"]
        self.cbb_them.configure(values=chua_co if chua_co else [""])
        self.var_them.set(chua_co[0] if chua_co else "")

    def _bao_doi(self):
        if self.khi_xong:
            self.khi_xong()

    # ------------------------------------------------------------ thao tác
    def them(self):
        ten = self.var_them.get().strip()
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
