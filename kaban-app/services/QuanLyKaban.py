from datetime import datetime
from models.DuAn import DuAn
from models.CongViec import CongViec, CongViecKhan


class QuanLyKanban:
    def __init__(self, bo_luu_tru):
        self.bo_luu_tru = bo_luu_tru
        self.danh_sach_du_an = self._nap_du_lieu()
        self.nguoi_dung_hien_tai = None

    def _nap_du_lieu(self):
        try:
            du_lieu = self.bo_luu_tru.doc_json("du_an.json")
            if not isinstance(du_lieu, list):
                return []
            danh_sach = []
            for item in du_lieu:
                if isinstance(item, dict):
                    da = DuAn.from_dict(item)
                    if da is not None:
                        danh_sach.append(da)
            return danh_sach
        except (FileNotFoundError, ValueError, KeyError, TypeError) as loi:
            print(f"Lỗi khi nạp dữ liệu dự án: {loi}")
            return []

    def _luu_du_lieu(self):
        try:
            du_lieu = [du_an.to_dict() for du_an in self.danh_sach_du_an]
            self.bo_luu_tru.ghi_json("du_an.json", du_lieu)
            return True
        except (OSError, ValueError, TypeError) as loi:
            print(f"Lỗi khi lưu dữ liệu dự án: {loi}")
            return False

    def tao_du_an(self, ma_du_an, ten_du_an, danh_sach_cot=None):
        """UI gọi để tạo mới một dự án; gọi DuAn và lưu vào bộ lưu trữ."""
        if self.tim_du_an_theo_ma(ma_du_an) is not None:
            print(f"Mã dự án '{ma_du_an}' đã tồn tại")
            return None

        du_an = DuAn(ma_du_an=ma_du_an, ten_du_an=ten_du_an, danh_sach_cot=danh_sach_cot)
        if du_an.ma_du_an is None:
            return None

        self.danh_sach_du_an.append(du_an)
        if self._luu_du_lieu():
            return du_an

        self.danh_sach_du_an.remove(du_an)
        return None

    def tim_du_an_theo_ma(self, ma_du_an):
        """UI gọi để tìm kiếm dự án theo mã trong danh sách dự án hiện có."""
        for du_an in self.danh_sach_du_an:
            if du_an.ma_du_an == ma_du_an:
                return du_an
        return None

    def dang_nhap(self, ten_dang_nhap, mat_khau):
        """UI gọi để xác thực đăng nhập người dùng qua tầng lưu trữ thành viên."""
        try:
            danh_sach_thanh_vien = self.bo_luu_tru.doc_danh_sach_thanh_vien()
        except Exception as loi:
            print(f"Lỗi khi đọc danh sách thành viên: {loi}")
            return False

        if not isinstance(danh_sach_thanh_vien, list):
            print("Danh sách thành viên không hợp lệ")
            return False

        thanh_vien = next(
            (tv for tv in danh_sach_thanh_vien if getattr(tv, "ten_dang_nhap", None) == ten_dang_nhap),
            None
        )
        if thanh_vien is None:
            print(f"Không tìm thấy tên đăng nhập '{ten_dang_nhap}'")
            return False

        if not thanh_vien.kiem_tra_mat_khau(mat_khau):
            print("Sai mật khẩu")
            return False

        self.nguoi_dung_hien_tai = thanh_vien
        return True

    def dang_xuat(self):
        """UI gọi để đăng xuất tài khoản hiện tại."""
        self.nguoi_dung_hien_tai = None

    def kiem_tra_quyen_du_an(self, du_an):
        """Kiểm tra quyền truy cập dự án của người dùng hiện tại."""
        if self.nguoi_dung_hien_tai is None:
            print("Bạn chưa đăng nhập")
            return False

        if du_an is None:
            return False

        vai_tro = getattr(self.nguoi_dung_hien_tai, "vai_tro", None)
        if vai_tro == "quan_tri":
            return True

        ten_dang_nhap = getattr(self.nguoi_dung_hien_tai, "ten_dang_nhap", None)
        if ten_dang_nhap and ten_dang_nhap in (du_an.thanh_vien_tham_gia or []):
            return True

        print("Bạn không có quyền truy cập dự án này")
        return False

    def kiem_tra_quyen_cong_viec(self, cong_viec):
        """Kiểm tra quyền thao tác trên công việc của người dùng hiện tại."""
        if self.nguoi_dung_hien_tai is None:
            print("Bạn chưa đăng nhập")
            return False
        if cong_viec is None:
            return False

        vai_tro = getattr(self.nguoi_dung_hien_tai, "vai_tro", None)
        if vai_tro == "quan_tri":
            return True

        ten_dang_nhap = getattr(self.nguoi_dung_hien_tai, "ten_dang_nhap", None)
        if ten_dang_nhap and cong_viec.nguoi_phu_trach == ten_dang_nhap:
            return True

        print("Bạn không có quyền thao tác trên công việc này")
        return False

    def tao_cong_viec(self, du_an, du_lieu, la_cong_viec_khan=False):
        """UI gọi để tạo mới công việc trong dự án; khởi tạo model CongViec và lưu trữ."""
        if not self.kiem_tra_quyen_du_an(du_an):
            return False

        if not isinstance(du_lieu, dict):
            print("Dữ liệu công việc không hợp lệ")
            return False

        ma_cong_viec = du_lieu.get("ma_cong_viec", du_lieu.get("MaCongViec"))
        tieu_de = du_lieu.get("tieu_de", du_lieu.get("TieuDe"))
        mo_ta = du_lieu.get("mo_ta", du_lieu.get("MoTa", ""))
        nguoi_phu_trach = du_lieu.get("nguoi_phu_trach", du_lieu.get("NguoiPhuTrach"))
        ngay_bat_dau = du_lieu.get("ngay_bat_dau", du_lieu.get("NgayBatDau"))
        ngay_ket_thuc = du_lieu.get("ngay_ket_thuc", du_lieu.get("NgayKetThuc"))
        trang_thai = du_lieu.get("trang_thai", du_lieu.get("TrangThai", "Cần làm"))
        muc_uu_tien = du_lieu.get("muc_uu_tien", du_lieu.get("MucUuTien", "Trung bình"))
        nhan = du_lieu.get("nhan", du_lieu.get("Nhan", "Backend"))

        if la_cong_viec_khan or muc_uu_tien == "Khẩn":
            cv = CongViecKhan(
                ma_cong_viec=ma_cong_viec,
                tieu_de=tieu_de,
                mo_ta=mo_ta,
                nguoi_phu_trach=nguoi_phu_trach,
                ngay_bat_dau=ngay_bat_dau,
                ngay_ket_thuc=ngay_ket_thuc,
                trang_thai=trang_thai,
                nhan=nhan
            )
        else:
            cv = CongViec(
                ma_cong_viec=ma_cong_viec,
                tieu_de=tieu_de,
                mo_ta=mo_ta,
                nguoi_phu_trach=nguoi_phu_trach,
                ngay_bat_dau=ngay_bat_dau,
                ngay_ket_thuc=ngay_ket_thuc,
                trang_thai=trang_thai,
                muc_uu_tien=muc_uu_tien,
                nhan=nhan
            )

        if cv.ma_cong_viec is None:
            return False

        if not du_an.them_cong_viec(cv):
            return False

        if not self._luu_du_lieu():
            du_an.xoa_cong_viec(cv.ma_cong_viec)
            return False

        return True

    def cap_nhat_cong_viec(self, du_an, ma_cong_viec, du_lieu_moi):
        """UI gọi để cập nhật công việc; kiểm tra quyền, gọi model cập nhật và lưu trữ."""
        if du_an is None:
            print("Dự án không hợp lệ")
            return False

        cv = du_an.tim_cong_viec_theo_ma(ma_cong_viec)
        if cv is None:
            print(f"Không tìm thấy công việc '{ma_cong_viec}' trong dự án")
            return False

        if not self.kiem_tra_quyen_cong_viec(cv):
            return False

        if not isinstance(du_lieu_moi, dict):
            print("Dữ liệu cập nhật không hợp lệ")
            return False

        du_lieu_model = {
            "TieuDe": du_lieu_moi.get("tieu_de", du_lieu_moi.get("TieuDe", cv.tieu_de)),
            "MoTa": du_lieu_moi.get("mo_ta", du_lieu_moi.get("MoTa", cv.mo_ta)),
            "NguoiPhuTrach": du_lieu_moi.get("nguoi_phu_trach", du_lieu_moi.get("NguoiPhuTrach", cv.nguoi_phu_trach)),
            "NgayBatDau": du_lieu_moi.get("ngay_bat_dau", du_lieu_moi.get("NgayBatDau", cv.ngay_bat_dau)),
            "NgayKetThuc": du_lieu_moi.get("ngay_ket_thuc", du_lieu_moi.get("NgayKetThuc", cv.ngay_ket_thuc)),
            "TrangThai": du_lieu_moi.get("trang_thai", du_lieu_moi.get("TrangThai", cv.trang_thai)),
            "MucUuTien": du_lieu_moi.get("muc_uu_tien", du_lieu_moi.get("MucUuTien", cv.muc_uu_tien)),
            "Nhan": du_lieu_moi.get("nhan", du_lieu_moi.get("Nhan", cv.nhan)),
        }
        cv.cap_nhat_cong_viec(du_lieu_model)
        return self._luu_du_lieu()

    def xoa_cong_viec(self, du_an, ma_cong_viec):
        """UI gọi để xóa công việc; chỉ quản trị viên có quyền và lưu dữ liệu sau khi xóa."""
        if self.nguoi_dung_hien_tai is None:
            print("Bạn chưa đăng nhập")
            return False

        vai_tro = getattr(self.nguoi_dung_hien_tai, "vai_tro", None)
        if vai_tro != "quan_tri":
            print("Chỉ quản trị viên mới có quyền xóa công việc")
            return False

        if du_an is None:
            print("Dự án không hợp lệ")
            return False

        if not du_an.xoa_cong_viec(ma_cong_viec):
            print(f"Không tìm thấy công việc '{ma_cong_viec}' để xóa")
            return False

        return self._luu_du_lieu()

    def chuyen_trang_thai(self, du_an, ma_cong_viec, trang_thai_moi):
        """UI gọi để chuyển cột Kanban; kiểm tra quyền, đổi trạng thái, ghi nhật ký và lưu dữ liệu."""
        if du_an is None:
            print("Dự án không hợp lệ")
            return False

        cv = du_an.tim_cong_viec_theo_ma(ma_cong_viec)
        if cv is None:
            print(f"Không tìm thấy công việc '{ma_cong_viec}'")
            return False

        if not self.kiem_tra_quyen_cong_viec(cv):
            return False

        trang_thai_cu, trang_thai_cap_nhat = cv.chuyen_trang_thai(trang_thai_moi)

        ten_dang_nhap = getattr(self.nguoi_dung_hien_tai, "ten_dang_nhap", "unknown")
        du_lieu_log = {
            "ten_dang_nhap": ten_dang_nhap,
            "thoi_gian": datetime.now().isoformat(),
            "ma_cong_viec": ma_cong_viec,
            "trang_thai_cu": trang_thai_cu,
            "trang_thai_moi": trang_thai_cap_nhat,
        }
        try:
            self.bo_luu_tru.ghi_nhat_ky(du_lieu_log)
        except Exception as loi:
            print(f"Lỗi ghi nhật ký: {loi}")

        return self._luu_du_lieu()

    def tim_kiem_cong_viec(self, du_an, tu_khoa):
        """UI gọi để tìm kiếm công việc theo từ khóa tiêu đề hoặc mã việc trong dự án."""
        if du_an is None or not hasattr(du_an, "danh_sach_cong_viec"):
            return []

        if not tu_khoa or not str(tu_khoa).strip():
            return list(du_an.danh_sach_cong_viec)

        tu_khoa_str = str(tu_khoa).lower().strip()
        return [
            cv for cv in du_an.danh_sach_cong_viec
            if tu_khoa_str in str(cv.tieu_de or "").lower()
            or tu_khoa_str in str(cv.ma_cong_viec or "").lower()
        ]

    def loc_theo_thanh_vien(self, du_an, ten_dang_nhap):
        """UI gọi để lọc danh sách công việc theo tên người phụ trách trong dự án."""
        if du_an is None or not hasattr(du_an, "danh_sach_cong_viec") or not ten_dang_nhap:
            return []

        user_str = str(ten_dang_nhap).strip().lower()
        return [
            cv for cv in du_an.danh_sach_cong_viec
            if str(cv.nguoi_phu_trach or "").strip().lower() == user_str
        ]

    def loc_theo_nhan(self, du_an, ten_nhan):
        """UI gọi để lọc danh sách công việc theo nhãn trong dự án."""
        if du_an is None or not hasattr(du_an, "danh_sach_cong_viec") or not ten_nhan:
            return []

        return [
            cv for cv in du_an.danh_sach_cong_viec
            if cv.nhan == ten_nhan
        ]

    def loc_theo_muc_uu_tien(self, du_an, muc_uu_tien):
        """UI gọi để lọc danh sách công việc theo mức ưu tiên trong dự án."""
        if du_an is None or not hasattr(du_an, "danh_sach_cong_viec") or not muc_uu_tien:
            return []

        return [
            cv for cv in du_an.danh_sach_cong_viec
            if cv.muc_uu_tien == muc_uu_tien
        ]

