"""ColumnDialog: Hộp thoại tạo mới hoặc đổi tên cột trạng thái trên bảng Kanban."""
import tkinter as tk
from ui.styles import theme
from utils.helpers import can_giua


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
