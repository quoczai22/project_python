"""Custom Widget CotKanban: một cột của bảng Kanban, có thanh cuộn dọc."""
import tkinter as tk
import weakref
from tkinter import ttk

from ui import theme
from ui.task_card import TaskCard

# Danh sách các cột đang tồn tại (WeakSet: cột bị huỷ thì tự biến mất khỏi danh sách)
_cac_cot = weakref.WeakSet()


def _cuon_toan_cuc(event):
    """Tìm cột đang nằm dưới con trỏ chuột rồi cuộn cột đó."""
    for cot in list(_cac_cot):
        if cot.winfo_exists() and cot.chua_diem(event.x_root, event.y_root):
            cot.cuon(event)
            break


class CotKanban(tk.Frame):
    """
    Một cột (ví dụ "Đang làm"), KẾ THỪA từ tk.Frame.
    Cấu trúc: tiêu đề (Label) + Canvas có Scrollbar chứa danh sách TaskCard.
    Mỗi cột là một Frame độc lập nên bảng Kanban chỉ việc xếp các cột cạnh nhau.
    """

    def __init__(self, master, ten_cot, khi_chon=None, khi_mo=None, khi_menu=None,
                 khi_keo=None, khi_tha=None):
        super().__init__(master, bg=theme.MAU_COT)
        self.ten_cot = ten_cot
        self.khi_chon = khi_chon
        self.khi_mo = khi_mo
        self.khi_menu = khi_menu
        self.khi_keo = khi_keo
        self.khi_tha = khi_tha
        self.cac_the = {}            # {ma_cong_viec: TaskCard}            # {ma_cong_viec: TaskCard}

        self._dung_giao_dien()
        self.dat_so_luong(0)
        self._bat_cuon_chuot()

    # ---------------------------------------------------------------- dựng giao diện
    def _dung_giao_dien(self):
        self.lbl_tieu_de = tk.Label(self, bg=theme.MAU_COT, fg=theme.MAU_CHU,
                                    font=theme.FONT_DAM, anchor="w")
        self.lbl_tieu_de.pack(fill="x", padx=10, pady=(10, 4))

        vung = tk.Frame(self, bg=theme.MAU_COT)
        vung.pack(fill="both", expand=True)

        self.thanh_cuon = ttk.Scrollbar(vung, orient="vertical")
        self.thanh_cuon.pack(side="right", fill="y")

        self.canvas = tk.Canvas(vung, bg=theme.MAU_COT, highlightthickness=0, width=260,
                                yscrollcommand=self.thanh_cuon.set)
        self.canvas.pack(side="left", fill="both", expand=True)
        self.thanh_cuon.configure(command=self.canvas.yview)

        # Frame bên trong Canvas: nơi thật sự chứa các thẻ
        self.ben_trong = tk.Frame(self.canvas, bg=theme.MAU_COT)
        self._cua_so_trong = self.canvas.create_window((0, 0), window=self.ben_trong, anchor="nw")

        # Khi nội dung đổi kích thước -> cập nhật vùng cuộn
        self.ben_trong.bind("<Configure>", self._cap_nhat_vung_cuon)
        # Khi Canvas đổi kích thước -> cho Frame trong rộng bằng Canvas
        self.canvas.bind("<Configure>", self._khi_canvas_doi_kich_thuoc)

        self.lbl_trong = tk.Label(self.ben_trong, text="Chưa có công việc",
                                  bg=theme.MAU_COT, fg=theme.MAU_CHU_PHU, font=theme.FONT_NHO)

    def _cap_nhat_vung_cuon(self, event):
        self.canvas.configure(scrollregion=self.canvas.bbox("all"))

    def _khi_canvas_doi_kich_thuoc(self, event):
        self.canvas.itemconfigure(self._cua_so_trong, width=event.width)

    # ---------------------------------------------------------------- dữ liệu
    def dat_so_luong(self, so_luong):
        self.lbl_tieu_de.configure(text=f"{self.ten_cot}  ({so_luong})")

    def xoa_het(self):
        for the in self.cac_the.values():
            the.destroy()
        self.cac_the.clear()

    def hien_thi(self, danh_sach_cong_viec):
        """Vẽ lại cột từ danh sách công việc (lấy từ backend)."""
        self.xoa_het()
        for cv in danh_sach_cong_viec:
            the = TaskCard(self.ben_trong, cv, khi_chon=self.khi_chon,
                           khi_mo=self.khi_mo, khi_menu=self.khi_menu)
            the.pack(fill="x", padx=8, pady=5)
            self.cac_the[cv.ma_cong_viec] = the

        if self.cac_the:
            self.lbl_trong.pack_forget()
        else:
            self.lbl_trong.pack(pady=20)
        self.dat_so_luong(len(self.cac_the))
        self.canvas.yview_moveto(0)
        the = TaskCard(self.ben_trong, cv, khi_chon=self.khi_chon,
                           khi_mo=self.khi_mo, khi_menu=self.khi_menu,
                           khi_keo=self.khi_keo, khi_tha=self.khi_tha)

    def chua_diem(self, x_root, y_root):
        """True nếu điểm (toạ độ trên màn hình) nằm trong cột này. Dùng cho kéo thả."""
        x, y = self.winfo_rootx(), self.winfo_rooty()
        return x <= x_root < x + self.winfo_width() and y <= y_root < y + self.winfo_height()
    def to_sang(self, bat):
        """Tô sáng cả cột khi đang rê thẻ vào (báo hiệu cột đích)."""
        mau = theme.MAU_COT_SANG if bat else theme.MAU_COT
        for w in (self, self.lbl_tieu_de, self.canvas, self.ben_trong, self.lbl_trong):
            w.configure(bg=mau)
    # ---------------------------------------------------------------- cuộn bằng chuột
    def _bat_cuon_chuot(self):
        # Chỉ gắn 1 lần cho cả ứng dụng. Không dùng <Enter>/<Leave> vì rê chuột
        # từ cột sang thẻ con cũng sinh <Leave>, làm mất cuộn.
        _cac_cot.add(self)
        if not self.bind_all("<MouseWheel>"):
            self.bind_all("<MouseWheel>", _cuon_toan_cuc)   # Windows, macOS
            self.bind_all("<Button-4>", _cuon_toan_cuc)     # Linux cuộn lên
            self.bind_all("<Button-5>", _cuon_toan_cuc)     # Linux cuộn xuống

    def cuon(self, event):
        # Nội dung ngắn hơn khung thì không cần cuộn
        if self.ben_trong.winfo_reqheight() <= self.canvas.winfo_height():
            return
        if event.num == 4:
            buoc = -1
        elif event.num == 5:
            buoc = 1
        else:
            buoc = -1 if event.delta > 0 else 1
        self.canvas.yview_scroll(buoc, "units")


# Chạy thử riêng file này:  python -m ui.cot_kanban
if __name__ == "__main__":
    from config import TEN_FILE_DU_AN, TEN_FILE_DU_LIEU_MOC
    from services.QuanLyKaban import QuanLyKanban

    ql = QuanLyKanban(TEN_FILE_DU_AN, TEN_FILE_DU_LIEU_MOC)
    ql.dang_nhap("admin", "123456")
    du_an = ql.lay_danh_sach_du_an()[0]

    goc = tk.Tk()
    goc.title("Thử CotKanban")
    goc.configure(bg=theme.MAU_NEN)
    goc.geometry("1150x600")
    theme.ap_dung_style()

    bang = tk.Frame(goc, bg=theme.MAU_NEN)
    bang.pack(fill="both", expand=True, padx=8, pady=8)

    for ten_cot in du_an.danh_sach_cot:
        cot = CotKanban(bang, ten_cot,
                        khi_mo=lambda c: print("Mở:", c.ma_cong_viec))
        cot.pack(side="left", fill="both", expand=True, padx=4)
        cong_viec_cot = du_an.lay_cong_viec_theo_trang_thai(ten_cot)
        # Cột "Cần làm": thêm vài việc giả (chỉ trong bộ nhớ, không lưu) để thấy thanh cuộn
        if ten_cot == "Cần làm":
            from models.CongViec import CongViecThuong
            cong_viec_cot = cong_viec_cot + [
                CongViecThuong(f"CV-{i}", f"Việc thử cuộn số {i}", "", "huy",
                               "2026-10-20", "2026-12-20")
                for i in range(100, 108)
            ]
        cot.hien_thi(cong_viec_cot)

    goc.mainloop()