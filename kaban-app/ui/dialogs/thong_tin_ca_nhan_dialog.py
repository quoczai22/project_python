"""ThongTinCaNhanDialog & DuyetSuaThongTinDialog: Luồng sửa thông tin người dùng có duyệt."""
import tkinter as tk
from tkinter import ttk, messagebox, simpledialog

from exceptions import KanbanException
from ui.styles import theme
from utils.helpers import can_giua


class ThongTinCaNhanDialog(tk.Toplevel):
    """Hộp thoại sửa thông tin cá nhân (Admin lưu thẳng, Leader/Thành viên gửi yêu cầu duyệt)."""

    def __init__(self, master, ql, khi_xong=None):
        super().__init__(master)
        self.ql, self.khi_xong = ql, khi_xong
        nd_ht = ql.nguoi_dung_hien_tai
        ds = ql.lay_danh_sach_nguoi_dung()
        self.nd = next((x for x in ds if x.ten_dang_nhap == nd_ht.ten_dang_nhap), nd_ht)

        self.title("Thông tin cá nhân")
        self.configure(bg=theme.MAU_THE)
        self.transient(master)
        self._dung_giao_dien()
        can_giua(self, 460, 360)
        self.wait_visibility()
        self.grab_set()

    def _dung_giao_dien(self):
        khung = tk.Frame(self, bg=theme.MAU_THE, padx=22, pady=16)
        khung.pack(fill="both", expand=True)

        tk.Label(khung, text=f"Tài khoản: {self.nd.ten_dang_nhap}  ({self.nd.vai_tro})",
                 bg=theme.MAU_THE, fg=theme.MAU_CHU_NHAN, font=theme.FONT_DAM, anchor="w").pack(fill="x", pady=(0, 10))

        tk.Label(khung, text="Họ và tên:", bg=theme.MAU_THE, fg=theme.MAU_CHU_NHAN, font=theme.FONT_NHO_DAM, anchor="w").pack(fill="x")
        self.var_ho_ten = tk.StringVar(value=self.nd.ho_ten)
        tk.Entry(khung, textvariable=self.var_ho_ten, font=theme.FONT_CHUAN).pack(fill="x", ipady=4, pady=(2, 10))

        tk.Label(khung, text="Email:", bg=theme.MAU_THE, fg=theme.MAU_CHU_NHAN, font=theme.FONT_NHO_DAM, anchor="w").pack(fill="x")
        self.var_email = tk.StringVar(value=self.nd.email)
        tk.Entry(khung, textvariable=self.var_email, font=theme.FONT_CHUAN).pack(fill="x", ipady=4, pady=(2, 10))

        ghi_chu = ""
        if self.nd.yeu_cau_sua_thong_tin:
            yc = self.nd.yeu_cau_sua_thong_tin
            ghi_chu = f"Đang chờ Admin duyệt: {yc.get('ho_ten', '')} | {yc.get('email', '')}"
        elif self.nd.ly_do_tu_choi_sua:
            ghi_chu = f"Yêu cầu gần nhất bị từ chối: {self.nd.ly_do_tu_choi_sua}"
        if ghi_chu:
            tk.Label(khung, text=ghi_chu, bg=theme.MAU_THE, fg=theme.MAU_CANH_BAO,
                     font=theme.FONT_NHO, anchor="w", wraplength=410, justify="left").pack(fill="x", pady=(0, 10))

        nut = tk.Frame(khung, bg=theme.MAU_THE)
        nut.pack(fill="x", side="bottom", pady=(10, 0))
        nhan_luu = "Lưu thay đổi" if self.nd.vai_tro == "quan_tri" else "Gửi yêu cầu duyệt"
        theme.tao_nut_chinh(nut, text=nhan_luu, command=self._luu, width=155, height=34).pack(side="right")
        theme.tao_nut_phu(nut, text="Đóng", command=self.destroy, width=85, height=34).pack(side="right", padx=(0, 8))

    def _luu(self):
        ho_ten, email = self.var_ho_ten.get().strip(), self.var_email.get().strip()
        try:
            if self.nd.vai_tro == "quan_tri":
                self.ql.sua_thong_tin_nguoi_dung(self.nd.ten_dang_nhap, ho_ten, email)
                messagebox.showinfo("Thành công", "Đã cập nhật thông tin cá nhân.", parent=self)
            else:
                self.ql.yeu_cau_sua_thong_tin(ho_ten, email)
                messagebox.showinfo("Đã gửi", "Yêu cầu sửa thông tin đang chờ Admin duyệt.", parent=self)
        except KanbanException as err:
            messagebox.showerror("Không thực hiện được", err.thong_diep, parent=self)
            return
        if self.khi_xong:
            self.khi_xong()
        self.destroy()


class DuyetSuaThongTinDialog(tk.Toplevel):
    """Màn hình Admin duyệt hoặc từ chối yêu cầu sửa thông tin cá nhân."""

    def __init__(self, master, ql, khi_xong=None):
        super().__init__(master)
        self.ql, self.khi_xong = ql, khi_xong
        self.title("Yêu cầu sửa thông tin người dùng")
        self.configure(bg=theme.MAU_THE)
        self.transient(master)

        cac_cot = (
            ("ten", "Tài khoản", 110),
            ("ho_ten", "Họ tên (Cũ -> Mới)", 250),
            ("email", "Email (Cũ -> Mới)", 270),
            ("thoi_gian", "Thời gian", 145),
        )
        self.tree = ttk.Treeview(self, columns=[c[0] for c in cac_cot], show="headings", selectmode="browse")
        for k, t, w in cac_cot:
            self.tree.heading(k, text=t)
            self.tree.column(k, width=w, anchor="w")
        self.tree.pack(fill="both", expand=True, padx=14, pady=(14, 8))

        hang = tk.Frame(self, bg=theme.MAU_THE, padx=14, pady=10)
        hang.pack(fill="x")
        theme.tao_nut_chinh(hang, text="Duyệt áp dụng", command=self._duyet, width=130, height=34).pack(side="left")
        theme.tao_nut_nguy_hiem(hang, text="Từ chối", command=self._tu_choi, width=100, height=34).pack(side="left", padx=8)
        theme.tao_nut_phu(hang, text="Đóng", command=self.destroy, width=85, height=34).pack(side="right")

        self._nap()
        can_giua(self, 820, 420)
        self.wait_visibility()
        self.grab_set()

    def _nap(self):
        self.tree.delete(*self.tree.get_children())
        try:
            ds = self.ql.lay_danh_sach_yeu_cau_sua_thong_tin()
        except KanbanException as err:
            messagebox.showerror("Không có quyền", err.thong_diep, parent=self)
            self.destroy()
            return
        for nd in ds:
            yc = nd.yeu_cau_sua_thong_tin or {}
            tg = str(yc.get("thoi_gian", ""))[:19].replace("T", " ")
            self.tree.insert("", "end", iid=nd.ten_dang_nhap, values=(
                nd.ten_dang_nhap,
                f"{nd.ho_ten} -> {yc.get('ho_ten', '')}",
                f"{nd.email} -> {yc.get('email', '')}",
                tg,
            ))

    def _duyet(self):
        chon = self.tree.selection()
        if not chon:
            return
        try:
            self.ql.duyet_sua_thong_tin(chon[0], chap_nhan=True)
        except KanbanException as err:
            messagebox.showerror("Không duyệt được", err.thong_diep, parent=self)
            return
        self._nap()
        if self.khi_xong:
            self.khi_xong()

    def _tu_choi(self):
        chon = self.tree.selection()
        if not chon:
            return
        ly_do = simpledialog.askstring("Từ chối yêu cầu", "Lý do từ chối:", parent=self)
        if ly_do is None:
            return
        try:
            self.ql.duyet_sua_thong_tin(chon[0], chap_nhan=False, ly_do=ly_do)
        except KanbanException as err:
            messagebox.showerror("Không từ chối được", err.thong_diep, parent=self)
            return
        self._nap()
        if self.khi_xong:
            self.khi_xong()


class TimKiemToanBoDialog(tk.Toplevel):
    """Tìm kiếm công việc qua mọi dự án người dùng có quyền xem; chọn kết quả để mở ngay."""

    def __init__(self, master, ql, khi_mo_ket_qua=None, tu_khoa_dau=""):
        super().__init__(master)
        self.ql, self.khi_mo_ket_qua = ql, khi_mo_ket_qua
        self._ket_qua = {}
        self.title("Tìm kiếm công việc qua mọi dự án")
        self.configure(bg=theme.MAU_THE)
        self.transient(master)

        hang_tim = tk.Frame(self, bg=theme.MAU_THE, padx=14, pady=12)
        hang_tim.pack(fill="x")
        self.var_kw = tk.StringVar(value=tu_khoa_dau)
        ent = tk.Entry(hang_tim, textvariable=self.var_kw, font=theme.FONT_CHUAN)
        ent.pack(side="left", fill="x", expand=True, ipady=4, padx=(0, 8))
        ent.bind("<KeyRelease>", lambda _e: self._tim())
        ent.bind("<Return>", lambda _e: self._tim())
        theme.tao_nut_chinh(hang_tim, text="Tìm kiếm", command=self._tim, width=96, height=32).pack(side="left")

        cac_cot = (
            ("du_an", "Dự án", 150),
            ("ma", "Mã CV", 80),
            ("tieu_de", "Tiêu đề", 260),
            ("trang_thai", "Trạng thái", 115),
            ("nguoi", "Phụ trách", 110),
        )
        self.tree = ttk.Treeview(self, columns=[c[0] for c in cac_cot], show="headings", selectmode="browse")
        for k, t, w in cac_cot:
            self.tree.heading(k, text=t)
            self.tree.column(k, width=w, anchor="w")
        self.tree.pack(fill="both", expand=True, padx=14, pady=(0, 8))
        self.tree.bind("<Double-1>", lambda _e: self._mo())

        hang_nut = tk.Frame(self, bg=theme.MAU_THE, padx=14, pady=10)
        hang_nut.pack(fill="x")
        self.lbl_kq = tk.Label(hang_nut, text="0 kết quả", bg=theme.MAU_THE, fg=theme.MAU_CHU_PHU, font=theme.FONT_NHO)
        self.lbl_kq.pack(side="left")
        theme.tao_nut_phu(hang_nut, text="Đóng", command=self.destroy, width=85, height=32).pack(side="right")
        theme.tao_nut_chinh(hang_nut, text="Mở công việc", command=self._mo, width=120, height=32).pack(side="right", padx=(0, 8))

        self._tim()
        can_giua(self, 780, 460)
        ent.focus_set()
        self.wait_visibility()
        self.grab_set()

    def _tim(self):
        self.tree.delete(*self.tree.get_children())
        self._ket_qua.clear()
        ds = self.ql.tim_kiem_toan_bo(self.var_kw.get())
        for idx, (da, cv) in enumerate(ds):
            iid = str(idx)
            self._ket_qua[iid] = (da, cv)
            self.tree.insert("", "end", iid=iid, values=(
                f"{da.ma_du_an} - {da.ten_du_an}", cv.ma_cong_viec, cv.tieu_de, cv.trang_thai, cv.nguoi_phu_trach
            ))
        self.lbl_kq.configure(text=f"{len(ds)} kết quả")

    def _mo(self):
        chon = self.tree.selection()
        if not chon or chon[0] not in self._ket_qua:
            return
        da, cv = self._ket_qua[chon[0]]
        self.destroy()
        if self.khi_mo_ket_qua:
            self.khi_mo_ket_qua(da, cv)
