"""Hộp thoại xem trước và chọn todo trước khi tạo thẻ Kanban."""
import tkinter as tk
from tkinter import ttk


class ApiPreviewDialog(tk.Toplevel):
    def __init__(self, master, todos, ids_da_ton_tai=(), thanh_vien=(), nguoi_mac_dinh=""):
        super().__init__(master)
        self.title("Xem trước công việc từ API")
        self.geometry("680x520")
        self.minsize(520, 360)
        self.transient(master)
        self.result = None
        self.vars = {}
        ton_tai = {int(ma) for ma in ids_da_ton_tai}

        ttk.Label(self, text="Chọn các công việc muốn đưa vào bảng Kanban:",
                  font=("Segoe UI", 11, "bold")).pack(anchor="w", padx=16, pady=(16, 8))
        khung = ttk.Frame(self)
        khung.pack(fill="both", expand=True, padx=16)
        canvas = tk.Canvas(khung, highlightthickness=0)
        cuon = ttk.Scrollbar(khung, orient="vertical", command=canvas.yview)
        danh_sach = ttk.Frame(canvas)
        danh_sach.bind("<Configure>", lambda _e: canvas.configure(scrollregion=canvas.bbox("all")))
        canvas.create_window((0, 0), window=danh_sach, anchor="nw")
        canvas.configure(yscrollcommand=cuon.set)
        canvas.pack(side="left", fill="both", expand=True)
        cuon.pack(side="right", fill="y")

        for todo in todos:
            ma = int(todo["id"])
            var = tk.BooleanVar(value=ma not in ton_tai)
            self.vars[ma] = var
            status = "Đã hoàn thành" if todo["hoan_thanh"] else "Chưa hoàn thành"
            nhan = f"#{ma}  {todo['tieu_de']}  —  {status}"
            if ma in ton_tai:
                nhan += "  (đã có trong dự án)"
            ttk.Checkbutton(danh_sach, text=nhan, variable=var).pack(anchor="w", fill="x", pady=4)

        tuy_chon = ttk.LabelFrame(self, text="Thiết lập luồng xử lý cho các việc được chọn", padding=8)
        tuy_chon.pack(fill="x", padx=16, pady=(10, 0))
        ttk.Label(tuy_chon, text="Người phụ trách").grid(row=0, column=0, sticky="w", padx=(0, 8))
        self.var_nguoi = tk.StringVar(value=nguoi_mac_dinh)
        ttk.Combobox(tuy_chon, textvariable=self.var_nguoi, values=list(thanh_vien),
                     state="readonly", width=22).grid(row=0, column=1, sticky="w", padx=(0, 16))
        ttk.Label(tuy_chon, text="Ưu tiên").grid(row=0, column=2, sticky="w", padx=(0, 8))
        self.var_uu_tien = tk.StringVar(value="Trung bình")
        ttk.Combobox(tuy_chon, textvariable=self.var_uu_tien,
                     values=("Thấp", "Trung bình", "Cao", "Khẩn"),
                     state="readonly", width=14).grid(row=0, column=3, sticky="w")
        tuy_chon.columnconfigure(4, weight=1)

        thanh = ttk.Frame(self)
        thanh.pack(fill="x", padx=16, pady=14)
        ttk.Button(thanh, text="Chọn tất cả", command=lambda: self._chon(True)).pack(side="left")
        ttk.Button(thanh, text="Bỏ chọn", command=lambda: self._chon(False)).pack(side="left", padx=8)
        ttk.Button(thanh, text="Hủy", command=self.destroy).pack(side="right")
        ttk.Button(thanh, text="Nhập đã chọn", command=self._xac_nhan).pack(side="right", padx=8)
        self.grab_set()
        self.wait_visibility()
        self.focus_set()

    def _chon(self, gia_tri):
        for var in self.vars.values():
            var.set(gia_tri)

    def _xac_nhan(self):
        self.result = {
            "ids": [ma for ma, var in self.vars.items() if var.get()],
            "nguoi_phu_trach": self.var_nguoi.get(),
            "muc_uu_tien": self.var_uu_tien.get(),
        }
        self.destroy()
