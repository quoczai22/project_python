"""ColumnDialog & ProjectDialogs: Quản lý cột trạng thái, tạo dự án và thành viên dự án."""
import re
import tkinter as tk
from tkinter import ttk, messagebox
import customtkinter as ctk

from config import TRANG_THAI_HOP_LE
from exceptions import (
    KanbanException, DuLieuKhongHopLeError, KhongCoQuyenError,
    XungDotDuLieuError, KhongTimThayError, LoiLuuTruError
)
from ui.styles import theme
from utils.helpers import can_giua

TEN_VAI_TRO = {"quan_tri": "Quản trị viên", "thanh_vien": "Thành viên"}
MAU_MA_DU_AN = r"^DA-\d{3,}$"


class ColumnDialog(tk.Toplevel):
    """
    Hộp thoại tạo mới hoặc đổi tên cột trạng thái trên bảng Kanban.
    Thiết kế phẳng corner_radius=0, bắt ngoại lệ và validate chặt chẽ.
    """

    def __init__(self, master, ten_cot_hien_tai="", danh_sach_cot_da_co=None, khi_xong=None):
        super().__init__(master)
        self.ten_cot_hien_tai = ten_cot_hien_tai
        self.danh_sach_cot_da_co = danh_sach_cot_da_co or []
        self.khi_xong = khi_xong
        self.ket_qua = None

        la_sua = bool(ten_cot_hien_tai)
        self.title("Đổi tên cột" if la_sua else "Thêm cột mới")
        self.configure(bg=theme.MAU_THE)
        self.resizable(False, False)
        self.transient(master)

        khung = tk.Frame(self, bg=theme.MAU_THE, padx=24, pady=20)
        khung.pack(fill="both", expand=True)

        lbl_tieu_de = tk.Label(
            khung, text="Đổi tên cột trạng thái" if la_sua else "Tạo cột trạng thái mới",
            bg=theme.MAU_THE, fg=theme.MAU_CHU, font=theme.FONT_DAM, anchor="w"
        )
        lbl_tieu_de.pack(fill="x", pady=(0, 12))

        tk.Label(
            khung, text="Tên cột trạng thái * (2-30 ký tự)", bg=theme.MAU_THE,
            fg=theme.MAU_CHU_NHAN, font=theme.FONT_NHO_DAM, anchor="w"
        ).pack(fill="x", pady=(0, 4))

        self.ent_ten = theme.tao_entry(khung, placeholder="VD: Cần xem xét, Đang kiểm thử...", cao=36)
        self.ent_ten.pack(fill="x", pady=(0, 8))
        if ten_cot_hien_tai:
            theme.dat_gia_tri_entry(self.ent_ten, ten_cot_hien_tai)

        self.lbl_loi = tk.Label(
            khung, text="", bg=theme.MAU_THE, fg="#dc2626",
            font=theme.FONT_NHO, anchor="w"
        )
        self.lbl_loi.pack(fill="x", pady=(0, 12))

        hang_nut = tk.Frame(khung, bg=theme.MAU_THE)
        hang_nut.pack(fill="x")

        theme.tao_nut_chinh(
            hang_nut, text="Lưu" if la_sua else "Thêm cột",
            command=self._luu, width=100, height=34
        ).pack(side="right")

        theme.tao_nut_phu(
            hang_nut, text="Hủy", command=self.destroy, width=80, height=34
        ).pack(side="right", padx=(0, 8))

        self.ent_ten.bind("<Return>", lambda _e: self._luu())
        self.bind("<Escape>", lambda _e: self.destroy())
        can_giua(self, 420, 220)
        self.ent_ten.focus_set()
        self.wait_visibility()
        self.grab_set()

    def _dat_loi(self, msg: str):
        self.lbl_loi.configure(text=msg)

    def _luu(self):
        self._dat_loi("")
        ten = self.ent_ten.get().strip()
        if not ten:
            self._dat_loi("Tên cột không được để trống.")
            self.ent_ten.focus_set()
            return
        if len(ten) < 2 or len(ten) > 30:
            self._dat_loi("Tên cột phải từ 2 đến 30 ký tự.")
            self.ent_ten.focus_set()
            return
        if any(c in ten for c in ["\n", "\r", "\t"]):
            self._dat_loi("Tên cột không được chứa ký tự xuống dòng hoặc tab.")
            self.ent_ten.focus_set()
            return

        ds_chuan = [c.strip().lower() for c in self.danh_sach_cot_da_co]
        ten_cu_chuan = self.ten_cot_hien_tai.strip().lower()
        if ten.lower() != ten_cu_chuan and ten.lower() in ds_chuan:
            self._dat_loi(f"Cột '{ten}' đã tồn tại trong quy trình.")
            self.ent_ten.focus_set()
            return

        self.ket_qua = ten
        self.destroy()
        if self.khi_xong:
            self.khi_xong(ten)


CotDialog = ColumnDialog


class TaoDuAnDialog(tk.Toplevel):
    """Tạo dự án mới (Dành cho Quản trị viên)."""

    def __init__(self, master, ql, khi_xong=None):
        super().__init__(master)
        self.ql = ql
        self.khi_xong = khi_xong

        self.title("Tạo dự án mới")
        self.configure(bg=theme.MAU_THE)
        self.resizable(False, False)
        self.transient(master)

        khung_ngoai = tk.Frame(self, bg=theme.MAU_THE)
        khung_ngoai.pack(fill="both", expand=True)

        theme.tao_header_figma(
            khung_ngoai, tieu_de="Khởi tạo dự án mới", badge_text="DA", cao=82
        )

        khung = tk.Frame(khung_ngoai, bg=theme.MAU_THE, padx=26, pady=18)
        khung.pack(fill="both", expand=True)

        tk.Label(
            khung, text="Mã dự án * (Định dạng DA-xxx, ví dụ DA-003)", bg=theme.MAU_THE,
            fg=theme.MAU_CHU_NHAN, font=theme.FONT_DAM, anchor="w"
        ).pack(fill="x", pady=(0, 4))
        self.ent_ma = theme.tao_entry(khung, placeholder="VD: DA-003", cao=38)
        self.ent_ma.pack(fill="x", pady=(0, 10))
        theme.dat_gia_tri_entry(self.ent_ma, self._sinh_ma())

        tk.Label(
            khung, text="Tên dự án * (3-100 ký tự)", bg=theme.MAU_THE,
            fg=theme.MAU_CHU_NHAN, font=theme.FONT_DAM, anchor="w"
        ).pack(fill="x", pady=(0, 4))
        self.ent_ten = theme.tao_entry(khung, placeholder="Nhập tên dự án...", cao=38)
        self.ent_ten.pack(fill="x", pady=(0, 8))

        self.lbl_loi = tk.Label(
            khung, text="", bg=theme.MAU_THE, fg="#dc2626",
            font=theme.FONT_NHO, anchor="w"
        )
        self.lbl_loi.pack(fill="x", pady=(0, 8))

        tk.Label(
            khung, text="Quy trình cột Kanban mặc định", bg=theme.MAU_THE,
            fg=theme.MAU_CHU_NHAN, font=theme.FONT_DAM, anchor="w"
        ).pack(fill="x", pady=(0, 4))
        khung_cot = ctk.CTkFrame(khung, fg_color=theme.MAU_CHINH_NHAT, corner_radius=0)
        khung_cot.pack(fill="x", pady=(0, 16))
        tk.Label(
            khung_cot, text="   →   ".join(TRANG_THAI_HOP_LE),
            bg=theme.MAU_CHINH_NHAT, fg=theme.MAU_CHINH_DAM,
            font=theme.FONT_DAM, pady=9
        ).pack()

        tk.Frame(khung, bg="#edf1f4", height=1).pack(fill="x", pady=(2, 12))
        hang_nut = tk.Frame(khung, bg=theme.MAU_THE)
        hang_nut.pack(fill="x")

        theme.tao_nut_chinh(
            hang_nut, text="Tạo dự án", command=self.luu, width=128, height=38
        ).pack(side="right")

        theme.tao_nut_phu(
            hang_nut, text="Hủy", command=self.destroy, width=96, height=38
        ).pack(side="right", padx=(0, 8))

        self.ent_ten.bind("<Return>", lambda _e: self.luu())
        self.bind("<Escape>", lambda _e: self.destroy())
        can_giua(self, 520, 460)
        self.ent_ten.focus_set()
        self.wait_visibility()
        self.grab_set()

    def _sinh_ma(self):
        so = []
        try:
            for d in self.ql.lay_danh_sach_du_an():
                m = re.fullmatch(r"DA-(\d+)", d.ma_du_an)
                if m:
                    so.append(int(m.group(1)))
        except Exception:
            pass
        return f"DA-{(max(so) + 1 if so else 1):03d}"

    def _dat_loi(self, msg: str):
        self.lbl_loi.configure(text=msg)

    def luu(self):
        self._dat_loi("")
        ma = self.ent_ma.get().strip().upper()
        ten = self.ent_ten.get().strip()

        if not re.fullmatch(MAU_MA_DU_AN, ma):
            self._dat_loi("Mã dự án phải theo định dạng DA-xxx (ví dụ DA-003, DA-101).")
            self.ent_ma.focus_set()
            return
        if not ten:
            self._dat_loi("Tên dự án không được để trống.")
            self.ent_ten.focus_set()
            return
        if len(ten) < 3 or len(ten) > 100:
            self._dat_loi("Tên dự án phải từ 3 đến 100 ký tự.")
            self.ent_ten.focus_set()
            return

        try:
            du_an = self.ql.tao_du_an(ma, ten)
        except DuLieuKhongHopLeError as loi:
            self._dat_loi(loi.thong_diep)
            return
        except XungDotDuLieuError as loi:
            self._dat_loi(loi.thong_diep)
            messagebox.showerror("Trùng lặp", loi.thong_diep, parent=self)
            return
        except KhongCoQuyenError as loi:
            messagebox.showerror("Từ chối quyền", loi.thong_diep, parent=self)
            return
        except LoiLuuTruError as loi:
            messagebox.showerror("Lỗi lưu trữ", loi.thong_diep, parent=self)
            return
        except KanbanException as loi:
            self._dat_loi(loi.thong_diep)
            return
        except Exception as e:
            messagebox.showerror("Lỗi hệ thống", f"Không thể tạo dự án: {e}", parent=self)
            return

        self.destroy()
        if self.khi_xong:
            self.khi_xong(du_an)


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
        theme.tao_nut_phu(
            hang_nut, text="Đóng", command=self.destroy, width=96, height=38
        ).pack(side="right")

    def _so_viec(self, ten):
        return sum(1 for cv in self.du_an.cong_viec if cv.nguoi_phu_trach == ten)

    def _cap_nhat_nut(self, _event=None):
        co_chon = bool(self.tree.selection())
        self.btn_xoa.configure(
            state="normal" if co_chon else "disabled",
            border_color=theme.MAU_VIEN_THE if co_chon else theme.MAU_VIEN
        )

    def _nap(self):
        self.tree.delete(*self.tree.get_children())
        for ten in self.du_an.thanh_vien_tham_gia:
            nd = self.nguoi_dung.get(ten)
            ho_ten = nd.ho_ten if nd else "(không còn tài khoản)"
            email = nd.email if nd else ""
            vai_tro = TEN_VAI_TRO.get(nd.vai_tro, nd.vai_tro) if nd else ""
            self.tree.insert(
                "", "end", iid=ten,
                values=(ten, ho_ten, email, vai_tro, self._so_viec(ten))
            )

        chua_co = [
            ten for ten, nd in self.nguoi_dung.items()
            if ten not in self.du_an.thanh_vien_tham_gia and nd.vai_tro != "quan_tri"
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
