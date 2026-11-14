"""ConfirmDialog: Hộp thoại xác nhận thao tác phẳng tối giản, hỗ trợ hủy/đồng ý."""
import tkinter as tk
import customtkinter as ctk

from ui.styles import theme


class ConfirmDialog(ctk.CTkToplevel):
    """
    Hộp thoại popup xác nhận hành động nguy hiểm (như xóa dự án, xóa công việc):
    - Thiết kế phẳng 100% (corner_radius=0)
    - Tùy biến màu nút xác nhận (nguy hiểm hoặc bình thường)
    """

    def __init__(self, master, tieu_de="Xác nhận", tin_nhan="Bạn có chắc chắn muốn thực hiện?",
                 nut_xac_nhan="Đồng ý", nut_huy="Hủy", nguy_hiem=True):
        super().__init__(master)
        self.ket_qua = False

        self.title(tieu_de)
        self.geometry("380x170")
        self.resizable(False, False)
        self.transient(master)
        self.configure(fg_color="#ffffff")

        # Căn giữa màn hình
        self.update_idletasks()
        x = master.winfo_rootx() + (master.winfo_width() - 380) // 2
        y = master.winfo_rooty() + (master.winfo_height() - 170) // 2
        self.geometry(f"+{max(x, 50)}+{max(y, 50)}")

        # Nội dung
        vung_chinh = tk.Frame(self, bg="#ffffff", padx=20, pady=16)
        vung_chinh.pack(fill="both", expand=True)

        lbl_tieu_de = tk.Label(
            vung_chinh, text=tieu_de,
            bg="#ffffff", fg="#0f172a",
            font=theme.FONT_DAM, anchor="w"
        )
        lbl_tieu_de.pack(fill="x", pady=(0, 6))

        lbl_msg = tk.Label(
            vung_chinh, text=tin_nhan,
            bg="#ffffff", fg="#475569",
            font=theme.FONT_CHUAN, anchor="w",
            wraplength=340, justify="left"
        )
        lbl_msg.pack(fill="x", pady=(0, 14))

        # Cụm nút
        cum_nut = tk.Frame(vung_chinh, bg="#ffffff")
        cum_nut.pack(side="bottom", fill="x")

        mau_btn_ok = "#dc2626" if nguy_hiem else "#6d669b"
        mau_btn_hover = "#b91c1c" if nguy_hiem else "#595284"

        btn_ok = ctk.CTkButton(
            cum_nut, text=nut_xac_nhan,
            command=self._dong_y,
            width=90, height=32, corner_radius=0,
            fg_color=mau_btn_ok, hover_color=mau_btn_hover,
            text_color="#ffffff", font=theme.FONT_NHO_DAM
        )
        btn_ok.pack(side="right", padx=(8, 0))

        btn_huy = ctk.CTkButton(
            cum_nut, text=nut_huy,
            command=self._huy,
            width=80, height=32, corner_radius=0,
            fg_color="#ffffff", hover_color="#f1f5f9",
            border_width=1, border_color="#cbd5e1",
            text_color="#64748b", font=theme.FONT_NHO_DAM
        )
        btn_huy.pack(side="right")

        self.grab_set()
        self.wait_window()

    def _dong_y(self):
        self.ket_qua = True
        self.destroy()

    def _huy(self):
        self.ket_qua = False
        self.destroy()


def xac_nhan(master, tin_nhan, tieu_de="Xác nhận", nguy_hiem=True) -> bool:
    """Hàm tiện ích hiển thị hộp thoại xác nhận và trả về True/False."""
    dlg = ConfirmDialog(master, tieu_de=tieu_de, tin_nhan=tin_nhan, nguy_hiem=nguy_hiem)
    return dlg.ket_qua
