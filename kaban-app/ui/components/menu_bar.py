"""AppMenuBar: Thành phần MenuBar hệ thống, dự án và công việc."""
import tkinter as tk


class AppMenuBar(tk.Menu):
    """
    Thanh menu chính của ứng dụng Kanban:
    - Menu Hệ thống (Đổi mật khẩu, Đăng xuất, Thoát)
    - Menu Dự án (Tạo dự án mới, Quản lý thành viên, Xuất báo cáo, Xóa dự án)
    - Menu Công việc (Thêm công việc, Lấy mẫu từ API, Xem thống kê)
    """

    def __init__(self, master, callbacks=None):
        super().__init__(master)
        self.master = master
        self.cb = callbacks or {}

        self._dung_menu()

    def _dung_menu(self):
        cau_truc = [
            ("Hệ thống", [
                ("Đổi mật khẩu...", self.cb.get("doi_mat_khau")),
                ("Đăng xuất", self.cb.get("dang_xuat")),
                None,
                ("Thoát", self.cb.get("thoat", self.master.destroy))
            ]),
            ("Dự án", [
                ("Tạo dự án mới", self.cb.get("tao_du_an")),
                ("Quản lý thành viên", self.cb.get("quan_ly_thanh_vien")),
                ("Xuất báo cáo tiến độ ra file...", self.cb.get("xuat_bao_cao")),
                None,
                ("Xóa dự án hiện tại", self.cb.get("xoa_du_an"))
            ]),
            ("Công việc", [
                ("Thêm công việc mới...", self.cb.get("them_cong_viec")),
                ("Lấy mẫu từ API...", self.cb.get("nhap_tu_api")),
                None,
                ("Xem thống kê", self.cb.get("mo_thong_ke"))
            ])
        ]

        for nhan, cac_muc in cau_truc:
            m = tk.Menu(self, tearoff=0)
            self.add_cascade(label=nhan, menu=m)
            for item in cac_muc:
                if item is None:
                    m.add_separator()
                else:
                    fn = item[1]
                    m.add_command(label=item[0], command=fn if fn else lambda: None)
