"""Danh sách việc chờ duyệt, đã hủy và yêu cầu nghiệp vụ (mở lại, gia hạn)."""
import re
import tkinter as tk
from tkinter import ttk, messagebox, simpledialog, filedialog

from config import SO_VIEC_API_TOI_DA
from exceptions import KanbanException
from services.nhap_api import lay_todos_tu_api, nhap_todos_da_chon
from services.thong_ke import xuat_bao_cao_file
from ui.dialogs.api_preview_dialog import ApiPreviewDialog


def nhap_tu_api_popup(parent, ql, du_an, lbl_trang_thai, ve_lai_cb):
    """Hộp thoại xem trước, chọn todo từ API công khai rồi nhập vào dự án đang mở."""
    if not du_an:
        messagebox.showinfo("Chưa có dự án", "Hãy chọn hoặc tạo dự án trước khi nhập từ API.", parent=parent)
        return
    so = simpledialog.askinteger("Nhập từ API", f"Số công việc muốn nhập (1–{SO_VIEC_API_TOI_DA}):",
                                 parent=parent, minvalue=1, maxvalue=SO_VIEC_API_TOI_DA, initialvalue=5)
    if so is None:
        return
    skip_cu = getattr(parent, "_api_skip", 0)
    skip = simpledialog.askinteger(
        "Trang dữ liệu API", "Bỏ qua bao nhiêu todo đầu tiên?",
        parent=parent, minvalue=0, maxvalue=10000, initialvalue=skip_cu
    )
    if skip is None:
        return
    lbl_trang_thai.configure(text="Đang tải dữ liệu từ API...")
    parent.configure(cursor="watch")
    parent.update_idletasks()
    try:
        todos, loi = lay_todos_tu_api(so, ql.bo_luu_tru, skip=skip)
        if loi:
            messagebox.showwarning("Không nhập được từ API", loi, parent=parent)
            return
        ids_da_ton_tai = [
            int(ma) for cv in du_an.cong_viec
            for ma in re.findall(r"\[API#(\d+)\]", cv.mo_ta or "")
        ]
        nd = ql.nguoi_dung_hien_tai
        nguoi_mac_dinh = nd.ten_dang_nhap
        if nd.vai_tro == "thanh_vien":
            thanh_vien = [nguoi_mac_dinh]
        elif nd.vai_tro == "truong_nhom":
            thanh_vien = [u for u in du_an.thanh_vien_tham_gia
                          if u == nguoi_mac_dinh or u in du_an.nhom.get(nguoi_mac_dinh, [])] or [nguoi_mac_dinh]
        else:
            thanh_vien = list(du_an.thanh_vien_tham_gia) or [nguoi_mac_dinh]
        parent.configure(cursor="")
        hop_thoai = ApiPreviewDialog(
            parent, todos, ids_da_ton_tai, thanh_vien=thanh_vien,
            nguoi_mac_dinh=nguoi_mac_dinh
        )
        parent.wait_window(hop_thoai)
        if hop_thoai.result is None:
            lbl_trang_thai.configure(text="Đã hủy xem trước dữ liệu API.")
            return
        tuy_chon = hop_thoai.result
        parent._api_skip = skip + len(todos)
        kq = nhap_todos_da_chon(
            ql, du_an, todos, tuy_chon["ids"],
            nguoi_phu_trach=tuy_chon["nguoi_phu_trach"],
            muc_uu_tien=tuy_chon["muc_uu_tien"]
        )
    except Exception as loi:
        messagebox.showerror("Lỗi hệ thống", f"Không thể nhập từ API: {loi}", parent=parent)
        return
    finally:
        parent.configure(cursor="")
    if kq.get("thong_bao"):
        messagebox.showwarning("Không nhập được từ API", kq["thong_bao"], parent=parent)
    else:
        msg = f"Đã thêm {kq['them']} việc. Bỏ qua {kq['trung']} việc trùng. Lỗi: {kq['loi']}."
        messagebox.showinfo("Nhập từ API", msg, parent=parent)
    ve_lai_cb()


def xuat_bao_cao_popup(parent, ql, du_an):
    """Hộp thoại chọn nơi lưu và xuất báo cáo tiến độ dự án (.txt/.csv)."""
    if not du_an:
        messagebox.showinfo("Chưa có dự án", "Vui lòng chọn hoặc tạo dự án trước khi xuất báo cáo.", parent=parent)
        return
    duong_dan = filedialog.asksaveasfilename(
        parent=parent, title="Lưu báo cáo tiến độ", initialfile=f"BaoCao_{du_an.ma_du_an}.txt",
        defaultextension=".txt", filetypes=[("Text File (*.txt)", "*.txt"), ("CSV File (*.csv)", "*.csv"), ("All Files (*.*)", "*.*")]
    )
    if not duong_dan:
        return
    try:
        xuat_bao_cao_file(du_an, duong_dan, ql)
        messagebox.showinfo("Thành công", f"Đã xuất báo cáo ra file:\n{duong_dan}", parent=parent)
    except Exception as e:
        messagebox.showerror("Lỗi", f"Không thể xuất báo cáo: {e}", parent=parent)


def yeu_cau_mo_lai_popup(parent, ql, du_an, cv):
    """Mở hộp thoại gửi yêu cầu mở lại công việc đã hoàn thành."""
    if not du_an or not cv:
        return
    ly_do = simpledialog.askstring("Mở lại", "Lý do mở lại công việc:", parent=parent)
    if ly_do is None:
        return
    try:
        ql.yeu_cau_mo_lai(du_an, cv.ma_cong_viec, ly_do)
    except KanbanException as err:
        messagebox.showerror("Không thực hiện được", err.thong_diep, parent=parent)
    else:
        messagebox.showinfo("Đã gửi", "Yêu cầu mở lại đang chờ duyệt", parent=parent)


def yeu_cau_gia_han_popup(parent, ql, du_an, cv):
    """Mở hộp thoại gửi yêu cầu gia hạn công việc quá hạn."""
    if not du_an or not cv:
        return
    han = simpledialog.askstring("Gia hạn", "Hạn mới (YYYY-MM-DD):", parent=parent)
    if han is None:
        return
    ly_do = simpledialog.askstring("Gia hạn", "Lý do gia hạn:", parent=parent)
    if ly_do is None:
        return
    try:
        ql.yeu_cau_gia_han(du_an, cv.ma_cong_viec, han, ly_do)
    except KanbanException as err:
        messagebox.showerror("Không thực hiện được", err.thong_diep, parent=parent)
    else:
        messagebox.showinfo("Đã gửi", "Yêu cầu gia hạn đang chờ duyệt", parent=parent)


class QuyTrinhDialog(tk.Toplevel):
    def __init__(self, master, ql, du_an, khi_xong=None):
        super().__init__(master)
        self.ql, self.du_an, self.khi_xong = ql, du_an, khi_xong
        self.title("Duyệt và khôi phục công việc")
        self.geometry("980x450")
        self.transient(master)
        cot = (
            ("ma", "Mã", 75),
            ("ten", "Công việc", 200),
            ("trang_thai", "Trạng thái", 95),
            ("duyet", "Duyệt", 90),
            ("yeu_cau", "Yêu cầu", 95),
            ("chi_tiet", "Chi tiết / Lý do", 360),
        )
        self.tree = ttk.Treeview(self, columns=[c[0] for c in cot], show="headings")
        for col, title, width in cot:
            self.tree.heading(col, text=title)
            self.tree.column(col, width=width, anchor="w")
        self.tree.pack(fill="both", expand=True, padx=12, pady=12)
        frame = tk.Frame(self)
        frame.pack(fill="x", padx=12, pady=8)
        for label, fn in (
            ("Duyệt việc", self._duyet),
            ("Từ chối việc", self._tu_choi),
            ("Gửi lại", self._gui_lai),
            ("Duyệt mở lại", self._mo_lai),
            ("Từ chối mở lại", self._tu_choi_mo_lai),
            ("Duyệt gia hạn", self._gia_han),
            ("Từ chối gia hạn", self._tu_choi_gia_han),
            ("Khôi phục", self._khoi_phuc),
        ):
            tk.Button(frame, text=label, command=fn).pack(side="left", padx=3)
        self.nap()

    def _mo_ta_chi_tiet(self, cv):
        cac_muc = []
        if cv.yeu_cau_mo_lai:
            yc = cv.yeu_cau_mo_lai
            cac_muc.append(f"Mở lại ({yc.get('nguoi', '')}): {yc.get('ly_do', '')}")
        if cv.yeu_cau_gia_han:
            yc = cv.yeu_cau_gia_han
            cac_muc.append(f"Gia hạn -> {yc.get('han_moi', '')} ({yc.get('nguoi', '')}): {yc.get('ly_do', '')}")
        if cv.trang_thai == "Đã hủy":
            cac_muc.append(f"Hủy bởi {cv.nguoi_huy}: {cv.ly_do_huy}")
        return " | ".join(cac_muc)

    def nap(self):
        self.tree.delete(*self.tree.get_children())
        for cv in self.du_an.cong_viec:
            if (cv.trang_thai == "Đã hủy" or cv.trang_thai_duyet in ("cho_duyet", "tu_choi") or
                    cv.yeu_cau_mo_lai or cv.yeu_cau_gia_han):
                yeu_cau = "Mở lại" if cv.yeu_cau_mo_lai else "Gia hạn" if cv.yeu_cau_gia_han else ""
                self.tree.insert("", "end", iid=cv.ma_cong_viec,
                                 values=(cv.ma_cong_viec, cv.tieu_de, cv.trang_thai,
                                         cv.trang_thai_duyet, yeu_cau, self._mo_ta_chi_tiet(cv)))

    def _chay(self, fn):
        chon = self.tree.selection()
        if not chon:
            messagebox.showinfo("Chưa chọn", "Hãy chọn công việc", parent=self)
            return
        try:
            fn(self.du_an, chon[0])
        except Exception as err:
            messagebox.showerror("Không thực hiện được", getattr(err, "thong_diep", str(err)), parent=self)
            return
        self.nap()
        if self.khi_xong:
            self.khi_xong()

    def _duyet(self):
        self._chay(self.ql.duyet_cong_viec)

    def _tu_choi(self):
        self._chay(lambda du_an, ma: self.ql.duyet_cong_viec(du_an, ma, False))

    def _gui_lai(self):
        self._chay(self.ql.gui_lai_cong_viec)

    def _mo_lai(self):
        self._chay(self.ql.duyet_mo_lai)

    def _tu_choi_mo_lai(self):
        self._chay(lambda du_an, ma: self.ql.duyet_mo_lai(du_an, ma, False))

    def _gia_han(self):
        self._chay(self.ql.duyet_gia_han)

    def _tu_choi_gia_han(self):
        self._chay(lambda du_an, ma: self.ql.duyet_gia_han(du_an, ma, False))

    def _khoi_phuc(self):
        self._chay(self.ql.khoi_phuc_cong_viec)
