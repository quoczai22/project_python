"""ThanhVienDuAnDialog: Xem, thêm, xóa thành viên của dự án."""
import tkinter as tk
import threading
import secrets
from tkinter import ttk, messagebox, simpledialog
from exceptions import (
    KanbanException, KhongCoQuyenError, XungDotDuLieuError,
    KhongTimThayError, LoiLuuTruError
)
from ui.styles import theme
from utils.helpers import can_giua

TEN_VAI_TRO = {"quan_tri": "Quản trị viên", "thanh_vien": "Thành viên", "truong_nhom": "Trưởng nhóm"}


class ThanhVienDuAnDialog(tk.Toplevel):
    """Xem, thêm, xóa thành viên của dự án kèm xử lý ngoại lệ chặt chẽ."""

    def __init__(self, master, ql, du_an, khi_xong=None):
        super().__init__(master)
        self.ql = ql
        self.du_an = du_an
        self.khi_xong = khi_xong
        self.nguoi_dung = {nd.ten_dang_nhap: nd for nd in ql.lay_danh_sach_nguoi_dung()}

        self.title(f"Thành viên - {du_an.ma_du_an}")
        self.configure(bg=theme.MAU_THE)
        self.minsize(700, 500)
        self.transient(master)
        self.var_them = tk.StringVar()

        self._dung_giao_dien()
        self._nap()
        self.bind("<Escape>", lambda _e: self.destroy())
        can_giua(self, 780, 560)
        self.wait_visibility()
        self.grab_set()

    def _dung_giao_dien(self):
        khung_ngoai = tk.Frame(self, bg=theme.MAU_THE)
        khung_ngoai.pack(fill="both", expand=True)

        theme.tao_header_figma(
            khung_ngoai, tieu_de=f"Thành viên: {self.du_an.ten_du_an}",
            badge_text="TV", cao=82, subtitle=f"Dự án {self.du_an.ma_du_an}"
        )

        khung = tk.Frame(khung_ngoai, bg=theme.MAU_THE, padx=26, pady=16)
        khung.pack(fill="both", expand=True)

        bang = tk.Frame(khung, bg=theme.MAU_THE)
        bang.pack(fill="both", expand=True, pady=(0, 12))
        bang.columnconfigure(0, weight=1)
        bang.rowconfigure(0, weight=1)

        cac_cot = (
            ("ten", "Tên đăng nhập", 125, "w"),
            ("ho_ten", "Họ và tên", 190, "w"),
            ("email", "Email", 190, "w"),
            ("vai_tro", "Vai trò", 120, "center"),
            ("so_viec", "Số việc", 80, "center"),
        )
        self.tree = ttk.Treeview(
            bang, columns=[c[0] for c in cac_cot],
            show="headings", height=7, selectmode="browse"
        )
        for khoa, tieu_de, rong, can in cac_cot:
            self.tree.heading(khoa, text=tieu_de)
            self.tree.column(khoa, width=rong, anchor=can)
        thanh = ttk.Scrollbar(bang, orient="vertical", command=self.tree.yview)
        self.tree.configure(yscrollcommand=thanh.set)
        self.tree.grid(row=0, column=0, sticky="nsew")
        thanh.grid(row=0, column=1, sticky="ns")
        self.tree.bind("<<TreeviewSelect>>", self._cap_nhat_nut)

        hang_them = tk.Frame(khung, bg=theme.MAU_THE)
        hang_them.pack(fill="x", pady=(4, 12))
        tk.Label(
            hang_them, text="Thêm thành viên:", bg=theme.MAU_THE,
            fg=theme.MAU_CHU_NHAN, font=theme.FONT_DAM
        ).pack(side="left")
        self.cbb_them = theme.tao_combobox(
            hang_them, values=[], variable=self.var_them, width=260, height=38
        )
        self.cbb_them.pack(side="left", padx=10, fill="x", expand=True)

        self.btn_them = theme.tao_nut_chinh(
            hang_them, text="+ Thêm vào dự án", command=self.them, width=164, height=38
        )
        self.btn_them.pack(side="left")

        tk.Frame(khung, bg="#edf1f4", height=1).pack(fill="x", pady=(0, 10))
        hang_nut = tk.Frame(khung, bg=theme.MAU_THE)
        hang_nut.pack(fill="x")
        self.btn_xoa = theme.tao_nut_nguy_hiem(
            hang_nut, text="Xóa thành viên đã chọn", command=self.xoa, width=216, height=38
        )
        self.btn_xoa.pack(side="left")
        la_admin = self.ql.nguoi_dung_hien_tai.vai_tro == "quan_tri"
        if la_admin:
            theme.tao_nut_phu(hang_nut, text="Cấp Leader", command=self.cap_leader,
                             width=110, height=38).pack(side="left", padx=5)
            theme.tao_nut_phu(hang_nut, text="Gán/Chuyển nhóm", command=self.gan_nhom,
                             width=140, height=38).pack(side="left", padx=5)
        theme.tao_nut_phu(
            hang_nut, text="Đóng", command=self.destroy, width=96, height=38
        ).pack(side="right")
        if la_admin:
            hang_quyen = tk.Frame(khung, bg=theme.MAU_THE)
            hang_quyen.pack(fill="x", pady=(8, 0))
            for text, fn in (("Tạo Leader", self.tao_leader), ("Thu hồi Leader", self.thu_hoi_leader),
                             ("Khóa tài khoản", self.khoa_tai_khoan), ("Mở khóa", self.mo_khoa_tai_khoan),
                             ("Tài khoản mẫu API", self.nhap_tai_khoan_mau)):
                theme.tao_nut_phu(hang_quyen, text=text, command=fn, width=130, height=34).pack(side="left", padx=3)

    def _so_viec(self, ten):
        return sum(1 for cv in self.du_an.cong_viec if cv.nguoi_phu_trach == ten and cv.trang_thai in ("Cần làm", "Đang làm", "Kiểm tra"))

    def cap_leader(self):
        chon = self.tree.selection()
        if not chon:
            return
        try:
            self.ql.cap_quyen_truong_nhom(self.du_an, chon[0])
        except KanbanException as err:
            messagebox.showerror("Không cấp được", err.thong_diep, parent=self)
            return
        self.nguoi_dung = {nd.ten_dang_nhap: nd for nd in self.ql.lay_danh_sach_nguoi_dung()}
        self._nap()

    def gan_nhom(self):
        chon = self.tree.selection()
        if not chon:
            return
        leader = simpledialog.askstring(
            "Gán / Chuyển nhóm",
            "Nhập tên đăng nhập Leader mới (để trống để gỡ khỏi nhóm):",
            parent=self
        )
        if leader is None:
            return
        try:
            self.ql.chuyen_thanh_vien_nhom(self.du_an, chon[0], leader.strip() or None)
        except KanbanException as err:
            messagebox.showerror("Không cập nhật được nhóm", err.thong_diep, parent=self)
            return
        self._nap()

    def tao_leader(self):
        ten = simpledialog.askstring("Tạo Leader", "Tên đăng nhập:", parent=self)
        if not ten:
            return
        mat_khau = simpledialog.askstring("Tạo Leader", "Mật khẩu tạm:", show="*", parent=self)
        if not mat_khau:
            return
        try:
            self.ql.tao_tai_khoan_truong_nhom(self.du_an, ten, mat_khau)
        except KanbanException as err:
            messagebox.showerror("Không tạo được", err.thong_diep, parent=self)
            return
        self.nguoi_dung = {nd.ten_dang_nhap: nd for nd in self.ql.lay_danh_sach_nguoi_dung()}
        self._nap()

    def thu_hoi_leader(self):
        chon = self.tree.selection()
        if not chon:
            return
        try:
            self.ql.thu_hoi_quyen_truong_nhom(chon[0])
        except KanbanException as err:
            messagebox.showerror("Không thu hồi được", err.thong_diep, parent=self)
            return
        self.nguoi_dung = {nd.ten_dang_nhap: nd for nd in self.ql.lay_danh_sach_nguoi_dung()}
        self._nap()

    def khoa_tai_khoan(self):
        self._dat_khoa(True)

    def mo_khoa_tai_khoan(self):
        self._dat_khoa(False)

    def _dat_khoa(self, bi_khoa):
        chon = self.tree.selection()
        if not chon:
            return
        try:
            self.ql.dat_khoa_tai_khoan(chon[0], bi_khoa)
        except KanbanException as err:
            messagebox.showerror("Không cập nhật được", err.thong_diep, parent=self)
            return
        self.nguoi_dung = {nd.ten_dang_nhap: nd for nd in self.ql.lay_danh_sach_nguoi_dung()}
        self._nap()

    def nhap_tai_khoan_mau(self):
        if not messagebox.askyesno("Tạo tài khoản demo", "Lấy tối đa 10 tài khoản mẫu từ JSONPlaceholder?", parent=self):
            return
        from services.api_mo_rong import lay_nguoi_dung_mau

        def worker():
            ds, loi = lay_nguoi_dung_mau()
            def luu():
                if not self.winfo_exists():
                    return
                if loi:
                    messagebox.showerror("Lỗi API", loi, parent=self)
                    return
                tao = []
                for muc in ds:
                    mat_khau = secrets.token_urlsafe(9)
                    try:
                        self.ql.dang_ky(muc["ten_dang_nhap"], mat_khau, muc["ho_ten"], muc["email"])
                        self.ql.them_thanh_vien_du_an(self.du_an, muc["ten_dang_nhap"])
                    except KanbanException:
                        continue
                    tao.append(f"{muc['ten_dang_nhap']}: {mat_khau}")
                self.nguoi_dung = {nd.ten_dang_nhap: nd for nd in self.ql.lay_danh_sach_nguoi_dung()}
                self._nap()
                messagebox.showinfo("Tài khoản demo đã tạo", "\n".join(tao) if tao else "Không có tài khoản mới", parent=self)
            self.after(0, luu)

        threading.Thread(target=worker, daemon=True).start()

    def _cap_nhat_nut(self, _event=None):
        co_chon = bool(self.tree.selection())
        self.btn_xoa.configure(
            state="normal" if co_chon else "disabled",
            border_color=theme.MAU_VIEN_THE if co_chon else theme.MAU_VIEN
        )

    def _nap(self):
        self.tree.delete(*self.tree.get_children())
        nhom_cua = {tv: ld for ld, ds in self.du_an.nhom.items() for tv in ds}
        for ten in self.du_an.thanh_vien_tham_gia:
            nd = self.nguoi_dung.get(ten)
            ho_ten = nd.ho_ten if nd else "(không còn tài khoản)"
            email = nd.email if nd else ""
            vai_tro = TEN_VAI_TRO.get(nd.vai_tro, nd.vai_tro) if nd else ""
            if ten in self.du_an.nhom:
                vai_tro = f"{vai_tro} ({len(self.du_an.nhom[ten])} TV)"
            elif ten in nhom_cua:
                vai_tro = f"{vai_tro} (Nhóm: {nhom_cua[ten]})"
            self.tree.insert(
                "", "end", iid=ten,
                values=(ten, ho_ten, email, vai_tro, self._so_viec(ten))
            )

        la_leader = self.ql.nguoi_dung_hien_tai.vai_tro == "truong_nhom"
        chua_co = [
            ten for ten, nd in self.nguoi_dung.items()
            if ten not in self.du_an.thanh_vien_tham_gia
            and nd.vai_tro != "quan_tri"
            and (not la_leader or nd.vai_tro != "truong_nhom")
        ]
        if chua_co:
            self.cbb_them.configure(values=chua_co, state="readonly")
            self.var_them.set(chua_co[0])
            self.btn_them.configure(state="normal", fg_color=theme.MAU_CHINH)
        else:
            self.cbb_them.configure(values=["(Đã tham gia hết)"], state="disabled")
            self.var_them.set("(Đã tham gia hết)")
            self.btn_them.configure(state="disabled", fg_color=theme.MAU_DISABLED_NEN)
        self._cap_nhat_nut()

    def _bao_doi(self):
        if self.khi_xong:
            self.khi_xong()

    def them(self):
        ten = self.var_them.get().strip()
        if not ten or ten == "(Đã tham gia hết)":
            messagebox.showinfo(
                "Không còn ai để thêm", "Tất cả tài khoản thành viên đã tham gia dự án này.", parent=self
            )
            return
        try:
            self.ql.them_thanh_vien_du_an(self.du_an, ten)
        except KhongCoQuyenError as loi:
            messagebox.showerror("Từ chối quyền", loi.thong_diep, parent=self)
            return
        except XungDotDuLieuError as loi:
            messagebox.showwarning("Đã tham gia", loi.thong_diep, parent=self)
            return
        except KhongTimThayError as loi:
            messagebox.showerror("Không tìm thấy", loi.thong_diep, parent=self)
            return
        except LoiLuuTruError as loi:
            messagebox.showerror("Lỗi lưu trữ", loi.thong_diep, parent=self)
            return
        except KanbanException as loi:
            messagebox.showerror("Lỗi thành viên", loi.thong_diep, parent=self)
            return
        except Exception as e:
            messagebox.showerror("Lỗi hệ thống", f"Không thể thêm thành viên: {e}", parent=self)
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
                "Hãy giao các việc đó cho người khác trước khi xóa.",
                parent=self
            )
            return
        if not messagebox.askyesno(
            "Xác nhận xóa",
            f"Xóa '{ten}' khỏi dự án {self.du_an.ma_du_an}?\nNgười này sẽ không còn nhìn thấy dự án.",
            icon="warning", parent=self
        ):
            return
        try:
            self.ql.xoa_thanh_vien_du_an(self.du_an, ten)
        except KhongCoQuyenError as loi:
            messagebox.showerror("Từ chối quyền", loi.thong_diep, parent=self)
            return
        except KhongTimThayError as loi:
            messagebox.showerror("Không tìm thấy", loi.thong_diep, parent=self)
            return
        except LoiLuuTruError as loi:
            messagebox.showerror("Lỗi lưu trữ", loi.thong_diep, parent=self)
            return
        except KanbanException as loi:
            messagebox.showerror("Lỗi thành viên", loi.thong_diep, parent=self)
            return
        except Exception as e:
            messagebox.showerror("Lỗi hệ thống", f"Không thể xóa thành viên: {e}", parent=self)
            return

        self._nap()
        self._bao_doi()
