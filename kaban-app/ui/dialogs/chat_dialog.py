"""ChatDialog: Hộp thoại nút "Chat" — bật máy chủ chat bằng file .bat hoặc kết nối tới máy chủ của người khác."""
import threading
import tkinter as tk

from services import chat_launcher
from ui.styles import theme
from utils.helpers import can_giua


class ChatDialog(tk.Toplevel):
    """Một nơi duy nhất để bật/tắt chat nhóm (Admin, Leader, Thành viên dùng chung)."""

    def __init__(self, master, ql, khi_xong=None):
        super().__init__(master)
        self.ql = ql
        self.khi_xong = khi_xong
        self._dang_xu_ly = False

        self.title("Chat nhóm")
        self.configure(bg=theme.MAU_THE)
        self.transient(master)
        self.resizable(False, False)
        self.protocol("WM_DELETE_WINDOW", self._dong)

        self._dung_giao_dien()
        self._cap_nhat_trang_thai()
        can_giua(self, 520, 560)
        self.bind("<Escape>", lambda _e: self._dong())
        self.wait_visibility()
        self.grab_set()

    # ---------- Giao diện ----------
    def _dung_giao_dien(self):
        theme.tao_header_figma(
            self, tieu_de="Chat nhóm", badge_text="CH", cao=74,
            subtitle="Nhắn tin giữa Admin, Leader, Thành viên"
        )
        than = tk.Frame(self, bg=theme.MAU_THE, padx=24, pady=12)
        than.pack(fill="both", expand=True)

        self.lbl_trang_thai = tk.Label(than, text="", bg=theme.MAU_THE, font=theme.FONT_DAM, anchor="w")
        self.lbl_trang_thai.pack(fill="x", pady=(0, 10))

        # --- Cách 1: máy này làm máy chủ ---
        tk.Label(than, text="1. Máy này làm máy chủ chat", bg=theme.MAU_THE, fg=theme.MAU_CHU_NHAN,
                 font=theme.FONT_DAM, anchor="w").pack(fill="x")
        tk.Label(than, text="Chỉ cần 1 máy trong nhóm làm việc này (ví dụ nhóm trưởng). Sẽ mở một cửa sổ đen, "
                            "đừng tắt nó trong lúc chat.",
                 bg=theme.MAU_THE, fg=theme.MAU_CHU_PHU, font=theme.FONT_NHO, anchor="w",
                 justify="left", wraplength=470).pack(fill="x", pady=(2, 6))
        self.btn_may_chu = theme.tao_nut_chinh(than, text="Bật máy chủ chat", command=self._bat_may_chu,
                                               width=170, height=34)
        self.btn_may_chu.pack(anchor="w")
        self.lbl_ip = tk.Label(than, text="", bg=theme.MAU_THE, fg=theme.MAU_CHINH_DAM,
                               font=theme.FONT_DAM, anchor="w", justify="left", wraplength=470)
        self.lbl_ip.pack(fill="x", pady=(6, 0))

        tk.Frame(than, bg="#edf1f4", height=1).pack(fill="x", pady=14)

        # --- Cách 2: kết nối tới máy chủ khác ---
        tk.Label(than, text="2. Kết nối tới máy chủ của người khác", bg=theme.MAU_THE, fg=theme.MAU_CHU_NHAN,
                 font=theme.FONT_DAM, anchor="w").pack(fill="x")
        tk.Label(than, text="Nhập IP mà máy chủ hiển thị. Hai máy phải cùng Wi-Fi / mạng LAN.",
                 bg=theme.MAU_THE, fg=theme.MAU_CHU_PHU, font=theme.FONT_NHO, anchor="w",
                 justify="left", wraplength=470).pack(fill="x", pady=(2, 6))
        hang = tk.Frame(than, bg=theme.MAU_THE)
        hang.pack(fill="x")
        self.ent_ip = theme.tao_entry(hang, placeholder="Ví dụ 192.168.100.232", cao=34)
        self.ent_ip.pack(side="left", fill="x", expand=True, padx=(0, 8))
        ip_da_luu = chat_launcher.doc_cau_hinh().get("ip_may_chu", "")
        if ip_da_luu:
            theme.dat_gia_tri_entry(self.ent_ip, ip_da_luu)
        self.btn_ket_noi = theme.tao_nut_chinh(hang, text="Kết nối", command=self._ket_noi_may_khac,
                                               width=100, height=34)
        self.btn_ket_noi.pack(side="right")
        self.ent_ip.bind("<Return>", lambda _e: self._ket_noi_may_khac())

        self.lbl_thong_bao = tk.Label(than, text="", bg=theme.MAU_THE, fg=theme.MAU_CHU_PHU,
                                      font=theme.FONT_NHO, anchor="w", justify="left", wraplength=470)
        self.lbl_thong_bao.pack(fill="x", pady=(10, 0))

        chan = tk.Frame(self, bg=theme.MAU_THE, padx=24, pady=10)
        chan.pack(side="bottom", fill="x")
        theme.tao_nut_phu(chan, text="Đóng", command=self._dong, width=90, height=34).pack(side="right")
        self.btn_ngat = theme.tao_nut_nguy_hiem(chan, text="Ngắt kết nối", command=self._ngat_ket_noi,
                                                width=120, height=34)
        self.btn_ngat.pack(side="right", padx=(0, 8))

    # ---------- Trạng thái ----------
    def _chat_hien_tai(self):
        return getattr(self.ql, "chat", None)

    def _cap_nhat_trang_thai(self):
        chat = self._chat_hien_tai()
        if chat is None:
            self.lbl_trang_thai.configure(text="○ Chưa kết nối (đang ngoại tuyến)", fg=theme.MAU_CHU_PHU)
            self.btn_ngat.pack_forget()
        else:
            self.lbl_trang_thai.configure(text=f"● Đã bật chat — {chat.url}", fg=theme.MAU_HOAN_THANH)
            if not self.btn_ngat.winfo_ismapped():
                self.btn_ngat.pack(side="right", padx=(0, 8))
        trang_thai = "disabled" if self._dang_xu_ly else "normal"
        self.btn_may_chu.configure(state=trang_thai)
        self.btn_ket_noi.configure(state=trang_thai)

    def _thong_bao(self, noi_dung, loi=False):
        if self.winfo_exists():
            self.lbl_thong_bao.configure(text=noi_dung, fg=theme.MAU_LOI if loi else theme.MAU_CHU_PHU)

    def _chay_nen(self, viec, khi_xong_viec):
        """Chạy `viec()` ở luồng nền (chỉ làm việc mạng, KHÔNG đụng tới tkinter) để giao diện không đơ.

        Luồng giao diện tự kiểm tra kết quả bằng after() rồi gọi `khi_xong_viec(ket_qua, loi)`.
        """
        self._dang_xu_ly = True
        self._cap_nhat_trang_thai()
        ket = {}

        def worker():
            try:
                ket["ket_qua"] = viec()
            except Exception as e:   # hiển thị cho người dùng thay vì để luồng chết im lặng
                ket["loi"] = e
            finally:
                ket["xong"] = True

        def cho_ket_qua():
            if not self.winfo_exists():
                return
            if not ket.get("xong"):
                self.after(80, cho_ket_qua)
                return
            self._dang_xu_ly = False
            khi_xong_viec(ket.get("ket_qua"), ket.get("loi"))
            self._cap_nhat_trang_thai()
            if self.khi_xong:
                self.khi_xong()

        threading.Thread(target=worker, daemon=True).start()
        self.after(80, cho_ket_qua)

    # ---------- Hành động ----------
    def _bat_may_chu(self):
        self._thong_bao("Đang bật máy chủ chat... (vài giây)")
        ip_lan = chat_launcher.lay_ip_lan()

        def viec():
            url = chat_launcher.bat_may_chu()          # chạy chat_server.bat nếu cổng chưa mở
            chat_launcher.ket_noi(self.ql, url)        # máy này nối vào server vừa bật
            return url

        def xong(_url, loi):
            if loi is not None:
                self._thong_bao(self._dich_loi(loi), loi=True)
                return
            self.lbl_ip.configure(text=f"Cho các máy khác nhập IP:  {ip_lan}")
            self._thong_bao("Xong. Đóng cửa sổ này, mở lại công việc để thấy khung bình luận ● Trực tuyến.")

        self._chay_nen(viec, xong)

    def _ket_noi_may_khac(self):
        try:
            url = chat_launcher.chuan_hoa_dia_chi(self.ent_ip.get())
        except ValueError as loi:
            self._thong_bao(str(loi), loi=True)
            return
        host, cong = chat_launcher.tach_url(url)
        self._thong_bao(f"Đang kết nối tới {host}...")

        def viec():
            if not chat_launcher.cong_dang_mo(host, cong, cho=2.0):
                raise ConnectionError(
                    f"Không nối được tới {host}:{cong}. Kiểm tra: (1) máy chủ đã bật chưa, "
                    "(2) hai máy cùng Wi-Fi/mạng, (3) IP đã đúng, (4) tường lửa của máy chủ."
                )
            chat_launcher.ket_noi(self.ql, url)
            return url

        def xong(_url, loi):
            if loi is not None:
                self._thong_bao(self._dich_loi(loi), loi=True)
                return
            chat_launcher.luu_cau_hinh(ip_may_chu=f"{host}:{cong}" if cong != chat_launcher.CONG_MAC_DINH else host)
            self._thong_bao("Đã kết nối. Mở lại công việc để thấy khung bình luận ● Trực tuyến.")

        self._chay_nen(viec, xong)

    def _ngat_ket_noi(self):
        chat_launcher.ngat_ket_noi(self.ql)
        self._thong_bao("Đã ngắt kết nối. Ứng dụng quay về chế độ ngoại tuyến.")
        self._cap_nhat_trang_thai()
        if self.khi_xong:
            self.khi_xong()

    @staticmethod
    def _dich_loi(loi: Exception) -> str:
        if isinstance(loi, ImportError):
            return "Chưa cài thư viện websockets. Chạy: pip install -r requirements.txt"
        return str(loi) or loi.__class__.__name__

    def _dong(self):
        self.destroy()
