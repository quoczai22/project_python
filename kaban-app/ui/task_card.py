"""Custom Widget TaskCard: thẻ công việc bo góc hiện đại trên bảng Kanban."""
import tkinter as tk
import customtkinter as ctk

from ui import theme


class TaskCard(ctk.CTkFrame):
    """
    Thẻ công việc, KẾ THỪA từ ctk.CTkFrame (bản chất là tk.Frame bo góc).
    - Thanh màu bên trái + badge bo tròn đổi theo mức ưu tiên.
    - Hiển thị mã, nhãn, tiêu đề, người phụ trách, hạn và cảnh báo đa hình.
    - Phát ra sự kiện qua các hàm callback: click, double-click, chuột phải, kéo-thả.
    """

    def __init__(self, master, cong_viec, khi_chon=None, khi_mo=None, khi_menu=None,
                 khi_keo=None, khi_tha=None):
        super().__init__(
            master,
            fg_color=theme.MAU_THE,
            corner_radius=10,
            border_width=1,
            border_color=theme.MAU_VIEN_THE,
            cursor="hand2"
        )
        self.cong_viec = cong_viec
        self.khi_chon = khi_chon      # click 1 lần
        self.khi_mo = khi_mo          # double-click
        self.khi_menu = khi_menu      # chuột phải
        self.khi_keo = khi_keo        # đang kéo (gọi liên tục khi rê chuột)
        self.khi_tha = khi_tha        # thả chuột sau khi kéo
        self._dang_chon = False
        self._diem_bam = None         # tọa độ màn hình lúc nhấn chuột
        self._dang_keo = False

        self._dung_giao_dien()
        self.cap_nhat(cong_viec)
        self._gan_su_kien(self)

        # Khi thẻ co giãn theo cột thì cho chữ tự xuống dòng theo chiều rộng
        self.bind("<Configure>", self._khi_doi_kich_thuoc, add="+")

    # ---------------------------------------------------------------- dựng giao diện
    def _dung_giao_dien(self):
        # Thanh màu bên trái chỉ thị mức độ ưu tiên
        self.thanh_mau = ctk.CTkFrame(self, width=5, corner_radius=3, fg_color=theme.MAU_CHINH)
        self.thanh_mau.pack(side="left", fill="y", padx=(6, 0), pady=8)

        self.noi_dung = tk.Frame(self, bg=theme.MAU_THE)
        self.noi_dung.pack(side="left", fill="both", expand=True, padx=(8, 10), pady=8)

        # Hàng 1: mã + nhãn (trái) và badge mức ưu tiên bo góc (phải)
        self.hang_tren = tk.Frame(self.noi_dung, bg=theme.MAU_THE)
        self.hang_tren.pack(fill="x")

        self.lbl_ma = tk.Label(
            self.hang_tren, bg=theme.MAU_THE, fg=theme.MAU_CHU_PHU,
            font=("Segoe UI", 8, "bold")
        )
        self.lbl_ma.pack(side="left")

        self.lbl_uu_tien = ctk.CTkLabel(
            self.hang_tren, text="", font=("Segoe UI", 10, "bold"),
            corner_radius=5, height=20, padx=7
        )
        self.lbl_uu_tien.pack(side="right")

        # Hàng 2: Tiêu đề công việc
        self.lbl_tieu_de = tk.Label(
            self.noi_dung, bg=theme.MAU_THE, fg=theme.MAU_CHU,
            font=theme.FONT_DAM, anchor="w", justify="left", wraplength=200
        )
        self.lbl_tieu_de.pack(fill="x", pady=(5, 4))

        # Đường kẻ mảnh ngăn cách thông tin phụ
        self.duong_ke = tk.Frame(self.noi_dung, bg=theme.MAU_VIEN, height=1)
        self.duong_ke.pack(fill="x", pady=(2, 4))

        # Hàng 3: Người phụ trách + số bình luận (nếu có)
        self.lbl_nguoi = tk.Label(
            self.noi_dung, bg=theme.MAU_THE, fg=theme.MAU_CHU_NHAN,
            font=theme.FONT_NHO, anchor="w"
        )
        self.lbl_nguoi.pack(fill="x")

        # Hàng 4: Hạn & Cảnh báo đa hình
        self.lbl_han = tk.Label(
            self.noi_dung, bg=theme.MAU_THE, font=theme.FONT_NHO,
            anchor="w", justify="left", wraplength=200
        )
        self.lbl_han.pack(fill="x", pady=(2, 0))

    # ---------------------------------------------------------------- hiển thị dữ liệu
    def cap_nhat(self, cong_viec):
        """Đổ dữ liệu của công việc lên thẻ."""
        cv = cong_viec
        self.cong_viec = cv
        mau = theme.MAU_UU_TIEN.get(cv.muc_uu_tien, theme.MAU_CHU_PHU)
        mau_chu = theme.MAU_CHU_TREN_UU_TIEN.get(cv.muc_uu_tien, "white")

        self.thanh_mau.configure(fg_color=mau)
        self.lbl_ma.configure(text=f"{cv.ma_cong_viec}  •  {cv.nhan or 'Không nhãn'}")
        self.lbl_uu_tien.configure(text=cv.muc_uu_tien, fg_color=mau, text_color=mau_chu)
        self.lbl_tieu_de.configure(text=cv.tieu_de)

        so_bl = len(getattr(cv, "danh_sach_binh_luan", []))
        phu_trach_txt = f"👤 {cv.nguoi_phu_trach}"
        if so_bl > 0:
            phu_trach_txt += f"   •   💬 {so_bl}"
        self.lbl_nguoi.configure(text=phu_trach_txt)

        if cv.is_hoan_thanh():
            self.lbl_han.configure(text="✓ Đã hoàn thành", fg=theme.MAU_HOAN_THANH)
        else:
            if cv.da_qua_han():
                mau_han = theme.MAU_LOI
            elif cv.muc_uu_tien == "Khẩn":
                mau_han = theme.MAU_CANH_BAO
            else:
                mau_han = theme.MAU_CHU_PHU
            self.lbl_han.configure(text=f"📅 {cv.ngay_ket_thuc} — {cv.canh_bao()}", fg=mau_han)

    def dat_chon(self, duoc_chon: bool):
        """Tô viền đậm màu Teal khi thẻ đang được chọn."""
        self._dang_chon = duoc_chon
        if duoc_chon:
            self.configure(border_color=theme.MAU_CHINH, border_width=2)
        else:
            self.configure(border_color=theme.MAU_VIEN_THE, border_width=1)

    # ---------------------------------------------------------------- sự kiện
    def _gan_su_kien(self, widget):
        """Gắn sự kiện cho thẻ và MỌI widget con (để bấm vào chữ cũng được)."""
        try:
            widget.bind("<Button-1>", self._xu_ly_click, add="+")
            widget.bind("<Double-Button-1>", self._xu_ly_double_click, add="+")
            widget.bind("<Button-3>", self._xu_ly_chuot_phai, add="+")
            widget.bind("<Button-2>", self._xu_ly_chuot_phai, add="+")
            widget.bind("<B1-Motion>", self._xu_ly_keo, add="+")
            widget.bind("<ButtonRelease-1>", self._xu_ly_tha, add="+")
            widget.bind("<Enter>", self._khi_re_vao, add="+")
            widget.bind("<Leave>", self._khi_re_ra, add="+")
        except Exception:
            pass
        for con in widget.winfo_children():
            self._gan_su_kien(con)

    def _xu_ly_click(self, event):
        self._diem_bam = (event.x_root, event.y_root)
        self._dang_keo = False
        if self.khi_chon:
            self.khi_chon(self.cong_viec)

    def _xu_ly_keo(self, event):
        if self._diem_bam is None:
            return
        if not self._dang_keo:
            dx = event.x_root - self._diem_bam[0]
            dy = event.y_root - self._diem_bam[1]
            if dx * dx + dy * dy < 36:
                return
            self._dang_keo = True
        if self.khi_keo:
            self.khi_keo(self.cong_viec, event)

    def _xu_ly_tha(self, event):
        if self._dang_keo:
            self._dang_keo = False
            if self.khi_tha:
                self.khi_tha(self.cong_viec, event)
        self._diem_bam = None

    def _xu_ly_double_click(self, event):
        if self.khi_mo:
            self.khi_mo(self.cong_viec)

    def _xu_ly_chuot_phai(self, event):
        if self.khi_menu:
            self.khi_menu(self.cong_viec, event)

    def _khi_re_vao(self, event):
        self._to_nen(theme.MAU_THE_HOVER)

    def _khi_re_ra(self, event):
        self._to_nen(theme.MAU_THE)

    def _to_nen(self, mau):
        """Đổi màu nền của thẻ và các nhãn con khi hover."""
        self.configure(fg_color=mau)
        for w in (self.noi_dung, self.hang_tren, self.lbl_ma,
                  self.lbl_tieu_de, self.lbl_nguoi, self.lbl_han):
            w.configure(bg=mau)

    def _khi_doi_kich_thuoc(self, event):
        wrap = max(event.width - 42, 100)
        self.lbl_tieu_de.configure(wraplength=wrap)
        self.lbl_han.configure(wraplength=wrap)
