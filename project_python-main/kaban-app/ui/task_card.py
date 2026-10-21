"""Custom Widget TaskCard: thẻ công việc trên bảng Kanban."""
import tkinter as tk

from ui import theme


class TaskCard(tk.Frame):
    """
    Thẻ công việc, KẾ THỪA từ tk.Frame (Custom Widget).
    - Thanh màu bên trái đổi theo mức ưu tiên.
    - Hiển thị mã, nhãn, tiêu đề, người phụ trách, hạn và cảnh báo.
    - Phát ra sự kiện qua các hàm callback: click, double-click, chuột phải.
    """

    def __init__(self, master, cong_viec, khi_chon=None, khi_mo=None, khi_menu=None,
                 khi_keo=None, khi_tha=None):
        super().__init__(master, bg=theme.MAU_THE, highlightthickness=1,
                         highlightbackground=theme.MAU_VIEN_THE, cursor="hand2")
        self.cong_viec = cong_viec
        self.khi_chon = khi_chon      # click 1 lần
        self.khi_mo = khi_mo          # double-click
        self.khi_menu = khi_menu      # chuột phải
        self.khi_keo = khi_keo        # đang kéo (gọi liên tục khi rê chuột)
        self.khi_tha = khi_tha        # thả chuột sau khi kéo
        self._dang_chon = False
        self._diem_bam = None         # toạ độ màn hình lúc nhấn chuột
        self._dang_keo = False

        self._dung_giao_dien()
        self.cap_nhat(cong_viec)
        self._gan_su_kien(self)

        # Khi thẻ co giãn theo cột thì cho chữ tự xuống dòng theo chiều rộng
        self.bind("<Configure>", self._khi_doi_kich_thuoc, add="+")

    # ---------------------------------------------------------------- dựng giao diện
    def _dung_giao_dien(self):
        self.thanh_mau = tk.Frame(self, width=6)
        self.thanh_mau.pack(side="left", fill="y")

        self.noi_dung = tk.Frame(self, bg=theme.MAU_THE)
        self.noi_dung.pack(side="left", fill="both", expand=True, padx=8, pady=6)

        # Hàng 1: mã + nhãn (trái) và badge mức ưu tiên (phải)
        hang_tren = tk.Frame(self.noi_dung, bg=theme.MAU_THE)
        hang_tren.pack(fill="x")
        self.lbl_ma = tk.Label(hang_tren, bg=theme.MAU_THE, fg=theme.MAU_CHU_PHU,
                               font=theme.FONT_NHO)
        self.lbl_ma.pack(side="left")
        self.lbl_uu_tien = tk.Label(hang_tren, font=theme.FONT_NHO, padx=6)
        self.lbl_uu_tien.pack(side="right")

        self.lbl_tieu_de = tk.Label(self.noi_dung, bg=theme.MAU_THE, fg=theme.MAU_CHU,
                                    font=theme.FONT_DAM, anchor="w", justify="left",
                                    wraplength=200)
        self.lbl_tieu_de.pack(fill="x", pady=(4, 2))

        self.lbl_nguoi = tk.Label(self.noi_dung, bg=theme.MAU_THE, fg=theme.MAU_CHU_PHU,
                                  font=theme.FONT_NHO, anchor="w")
        self.lbl_nguoi.pack(fill="x")

        self.lbl_han = tk.Label(self.noi_dung, bg=theme.MAU_THE, font=theme.FONT_NHO,
                                anchor="w", justify="left", wraplength=200)
        self.lbl_han.pack(fill="x")

    # ---------------------------------------------------------------- hiển thị dữ liệu
    def cap_nhat(self, cong_viec):
        """Đổ dữ liệu của công việc lên thẻ (gọi lại khi công việc thay đổi)."""
        cv = cong_viec
        self.cong_viec = cv
        mau = theme.MAU_UU_TIEN.get(cv.muc_uu_tien, theme.MAU_CHU_PHU)

        self.thanh_mau.configure(bg=mau)
        self.lbl_ma.configure(text=f"{cv.ma_cong_viec} • {cv.nhan or 'Không nhãn'}")
        self.lbl_uu_tien.configure(
            text=cv.muc_uu_tien, bg=mau,
            fg=theme.MAU_CHU_TREN_UU_TIEN.get(cv.muc_uu_tien, "white"))
        self.lbl_tieu_de.configure(text=cv.tieu_de)
        self.lbl_nguoi.configure(text=f"Phụ trách: {cv.nguoi_phu_trach}")

        if cv.is_hoan_thanh():
            self.lbl_han.configure(text="Đã hoàn thành", fg=theme.MAU_HOAN_THANH)
        else:
            # ĐA HÌNH: canh_bao() của CongViecThuong và CongViecKhan cho nội dung khác nhau
            if cv.da_qua_han():
                mau_han = theme.MAU_LOI
            elif cv.muc_uu_tien == "Khẩn":
                mau_han = theme.MAU_CANH_BAO
            else:
                mau_han = theme.MAU_CHU_PHU
            self.lbl_han.configure(text=f"Hạn {cv.ngay_ket_thuc}: {cv.canh_bao()}", fg=mau_han)

    def dat_chon(self, duoc_chon: bool):
        """Tô viền đậm khi thẻ đang được chọn."""
        self._dang_chon = duoc_chon
        if duoc_chon:
            self.configure(highlightbackground=theme.MAU_CHINH, highlightthickness=2)
        else:
            self.configure(highlightbackground=theme.MAU_VIEN_THE, highlightthickness=1)

    # ---------------------------------------------------------------- sự kiện
    def _gan_su_kien(self, widget):
        """Gắn sự kiện cho thẻ và MỌI widget con (để bấm vào chữ cũng được)."""
        widget.bind("<Button-1>", self._xu_ly_click, add="+")
        widget.bind("<Double-Button-1>", self._xu_ly_double_click, add="+")
        widget.bind("<Button-3>", self._xu_ly_chuot_phai, add="+")
        widget.bind("<Button-2>", self._xu_ly_chuot_phai, add="+")   # chuột phải trên macOS
        widget.bind("<B1-Motion>", self._xu_ly_keo, add="+")
        widget.bind("<ButtonRelease-1>", self._xu_ly_tha, add="+")
        widget.bind("<Enter>", self._khi_re_vao, add="+")
        widget.bind("<Leave>", self._khi_re_ra, add="+")
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
            if dx * dx + dy * dy < 36:      # nhích dưới 6px thì vẫn coi là click
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
        """Đổi màu nền của thẻ và các nhãn con (trừ thanh ưu tiên và badge)."""
        for w in (self, self.noi_dung, self.lbl_ma, self.lbl_tieu_de,
                  self.lbl_nguoi, self.lbl_han, self.lbl_ma.master):
            w.configure(bg=mau)

    def _khi_doi_kich_thuoc(self, event):
        wrap = max(event.width - 40, 80)
        self.lbl_tieu_de.configure(wraplength=wrap)
        self.lbl_han.configure(wraplength=wrap)


# Chạy thử riêng file này:  python -m ui.task_card
if __name__ == "__main__":
    from config import TEN_FILE_DU_AN, TEN_FILE_DU_LIEU_MOC
    from services.QuanLyKaban import QuanLyKanban

    ql = QuanLyKanban(TEN_FILE_DU_AN, TEN_FILE_DU_LIEU_MOC)
    ql.dang_nhap("admin", "123456")
    du_an = ql.lay_danh_sach_du_an()[0]

    goc = tk.Tk()
    goc.title("Thử TaskCard")
    goc.configure(bg=theme.MAU_COT)
    goc.geometry("340x640")
    theme.ap_dung_style()

    the_dang_chon = {"the": None}

    def chon(cv):
        if the_dang_chon["the"]:
            the_dang_chon["the"].dat_chon(False)
        the_dang_chon["the"] = ban_do[cv.ma_cong_viec]
        the_dang_chon["the"].dat_chon(True)
        print("Chọn:", cv.ma_cong_viec)

    ban_do = {}
    for cv in du_an.cong_viec[2:7]:
        the = TaskCard(goc, cv, khi_chon=chon,
                       khi_mo=lambda c: print("Mở:", c.ma_cong_viec),
                       khi_menu=lambda c, e: print("Chuột phải:", c.ma_cong_viec))
        the.pack(fill="x", padx=12, pady=5)
        ban_do[cv.ma_cong_viec] = the

    goc.mainloop()