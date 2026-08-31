import re
from datetime import datetime
from config import TRANG_THAI_HOP_LE

class DuAn:
    def __init__(self, maDuAn, tenDuAn, danhSachCot=None, thanhVienThamGia=None,danhSachCongViec=None,ngayTao=None):
        self.maDuAn = maDuAn
        self.tenDuAn = tenDuAn
        self.danhSachCot = danhSachCot if danhSachCot is not None else list(TRANG_THAI_HOP_LE)
        self.thanhVienThamGia = thanhVienThamGia if thanhVienThamGia is not None else []
        self.danhSachCongViec = danhSachCongViec if danhSachCongViec is not None else []
        self.ngayTao = ngayTao if ngayTao is not None else datetime.now().strftime("%Y-%m-%d")
        
    def __str__(self):
        return f"DuAn(MaDuAn={self.maDuAn}, TenDuAn={self.tenDuAn}, DanhSachCot={self.danhSachCot}, ThanhVienThamGia={self.thanhVienThamGia}, DanhSachCongViec={self.danhSachCongViec}, NgayTao={self.ngayTao})"
    
    def __repr__(self):
        return self.__str__()

    @property
    def maDuAn(self):
        return getattr(self, "_maDuAn", None)

    @maDuAn.setter
    def maDuAn(self, maDuAn):
        if not maDuAn or not re.match(r"^DA-\d{3,}$", str(maDuAn)):
            print(f"Mã dự án {maDuAn} sai định dạng (VD: DA-001)")
            self._maDuAn = None
            return
        self._maDuAn = str(maDuAn)

    @property
    def tenDuAn(self):
        return getattr(self, "_tenDuAn", None)

    @tenDuAn.setter
    def tenDuAn(self, tenDuAn):
        if not tenDuAn or not str(tenDuAn).strip():
            print("Tên dự án không được để trống")
            self._tenDuAn = ""
            return
        self._tenDuAn = str(tenDuAn).strip()
    
    @property
    def ngayTao(self):
        return getattr(self, "_ngayTao", None)

    @ngayTao.setter
    def ngayTao(self, ngayTao):
        try:
            if not re.fullmatch(r"\d{4}-\d{2}-\d{2}", str(ngayTao)):
                print("Ngày tạo phải có dạng YYYY-MM-DD")
                self._ngayTao = None
                return
            datetime.strptime(str(ngayTao), "%Y-%m-%d")
            self._ngayTao = str(ngayTao)
        except ValueError as loi:
            print(f"Ngày tạo không hợp lệ: {loi}")
            self._ngayTao = None

    @property
    def thanhVienThamGia(self):
        return getattr(self, "_thanhVienThamGia", None)

    @thanhVienThamGia.setter
    def thanhVienThamGia(self, thanhVienThamGia):
        if not isinstance(thanhVienThamGia, list):
            print("Danh sách thành viên phải là list")
            self._thanhVienThamGia = []
            return
        if any(not isinstance(thanh_vien, str) or not thanh_vien.strip()
               for thanh_vien in thanhVienThamGia):
            print("Mỗi thành viên phải là tên đăng nhập không rỗng")
            self._thanhVienThamGia = []
            return
        if len(thanhVienThamGia) != len(set(thanhVienThamGia)):
            print("Danh sách thành viên không được trùng")
            self._thanhVienThamGia = []
            return
        self._thanhVienThamGia = thanhVienThamGia

    @property
    def danhSachCongViec(self):
        return getattr(self, "_danhSachCongViec", None)

    @danhSachCongViec.setter
    def danhSachCongViec(self, danhSachCongViec):
        if not isinstance(danhSachCongViec, list):
            print("Danh sách công việc phải là list")
            self._danhSachCongViec = []
            return
        self._danhSachCongViec = danhSachCongViec

    @property
    def danhSachCot(self):
        return getattr(self, "_danhSachCot", None)

    @danhSachCot.setter
    def danhSachCot(self, danhSachCot):
        if not isinstance(danhSachCot, list) or not danhSachCot:
            print("Danh sách cột phải là list không rỗng")
            self._danhSachCot = list(TRANG_THAI_HOP_LE)
            return
        if len(danhSachCot) != len(set(danhSachCot)):
            print("Danh sách cột không được trùng")
            self._danhSachCot = list(TRANG_THAI_HOP_LE)
            return
        if any(cot not in TRANG_THAI_HOP_LE for cot in danhSachCot):
            print("Danh sách cột có trạng thái không hợp lệ")
            self._danhSachCot = list(TRANG_THAI_HOP_LE)
            return
        self._danhSachCot = danhSachCot

    @property
    def soLuongCongViec(self):
        return len(self.danhSachCongViec)

    @property
    def soLuongThanhVien(self):
        return len(self.thanhVienThamGia)

    def ThemCongViec(self, congViec):
        """Thêm công việc vào dự án, kiểm tra trùng mã và cột trạng thái hợp lệ."""
        from models.CongViec import CongViec

        if not isinstance(congViec, CongViec):
            print("Công việc phải là object CongViec")
            return False

        if self.TimCongViecTheoMa(congViec.MaCongViec) is not None:
            print(f"Mã công việc '{congViec.MaCongViec}' đã tồn tại")
            return False
        if congViec.TrangThai not in self.danhSachCot:
            print(f"Trạng thái '{congViec.TrangThai}' không thuộc danh sách cột của dự án này")
            return False
        self._danhSachCongViec.append(congViec)
        return True

    def XoaCongViec(self, maCongViec):
        """Xóa công việc theo mã; trả về True nếu tìm thấy và xóa thành công."""
        cong_viec = self.TimCongViecTheoMa(maCongViec)
        if cong_viec is None:
            print(f"Không tìm thấy công việc '{maCongViec}'")
            return False
        self._danhSachCongViec.remove(cong_viec)
        return True

    def TimCongViecTheoMa(self, maCongViec):
        """Tìm và trả về công việc theo mã; không có thì trả về None."""
        for cong_viec in self._danhSachCongViec:
            if cong_viec.MaCongViec == maCongViec:
                return cong_viec
        return None

    def ThemThanhVien(self, tenDangNhap):
        """Thêm username thành viên vào dự án."""
        if not isinstance(tenDangNhap, str) or not tenDangNhap.strip():
            print("Tên đăng nhập không được để trống")
            return False
        if tenDangNhap in self._thanhVienThamGia:
            print(f"Thành viên '{tenDangNhap}' đã có trong dự án")
            return False
        self._thanhVienThamGia.append(tenDangNhap.strip())
        return True

    def XoaThanhVien(self, tenDangNhap):
        """Xóa username khỏi dự án; trả về True nếu tìm thấy và xóa thành công."""
        if not isinstance(tenDangNhap, str) or not tenDangNhap.strip():
            return False
        ten_dang_nhap = tenDangNhap.strip()
        if ten_dang_nhap not in self._thanhVienThamGia:
            print(f"Không tìm thấy thành viên '{ten_dang_nhap}' trong dự án")
            return False
        self._thanhVienThamGia.remove(ten_dang_nhap)
        return True

    def LayCongViecTheoTrangThai(self, trangThai):
        """Lấy các công việc đang thuộc một cột Kanban."""
        if trangThai not in self.danhSachCot:
            print(f"Trạng thái '{trangThai}' không thuộc dự án")
            return []
        return [
            cong_viec for cong_viec in self._danhSachCongViec
            if cong_viec.TrangThai == trangThai
        ]

    def TimKiem(self, tuKhoa):
        """Tìm công việc theo tiêu đề hoặc mã, không phân biệt hoa thường."""
        if not tuKhoa or not str(tuKhoa).strip():
            return list(self._danhSachCongViec)
        tu_khoa = str(tuKhoa).lower().strip()
        return [
            cv for cv in self._danhSachCongViec
            if tu_khoa in str(cv.TieuDe or "").lower()
            or tu_khoa in str(cv.MaCongViec or "").lower()
        ]

    def LocTheoCot(self, tenCot):
        """Lọc công việc theo cột trạng thái."""
        return self.LayCongViecTheoTrangThai(tenCot)

    def LocTheoNguoiPhuTrach(self, tenDangNhap):
        """Lọc danh sách các công việc được giao cho một người phụ trách."""
        if not tenDangNhap or not str(tenDangNhap).strip():
            return []
        nguoi_pt = str(tenDangNhap).strip().lower()
        return [
            cv for cv in self._danhSachCongViec
            if str(cv.NguoiPhuTrach or "").strip().lower() == nguoi_pt
        ]

    def LocTheoNhan(self, tenNhan):
        """Lọc danh sách công việc theo nhãn."""
        if not tenNhan:
            return []
        return [
            cv for cv in self._danhSachCongViec
            if cv.Nhan == tenNhan
        ]

    def DemTheoCot(self):

        return {
            cot: len(self.LayCongViecTheoTrangThai(cot))
            for cot in self.danhSachCot
        }

    def DemQuaHan(self):
        """Đếm số công việc chưa hoàn thành nhưng đã quá hạn."""
        return len([
            cv for cv in self._danhSachCongViec
            if cv.DaQuaHan() and not cv.IsHoanThanh()
        ])

    def DemHoanThanh(self):
        """Đếm số công việc đã hoàn thành."""
        return len([
            cv for cv in self._danhSachCongViec
            if cv.IsHoanThanh()
        ])

    def LayCongViecCanCanhBao(self):

        ket_qua = []
        for cv in self._danhSachCongViec:
            if not cv.IsHoanThanh():
                thong_bao = cv.CanhBao()
                if thong_bao:
                    ket_qua.append((cv, thong_bao))
        return ket_qua

    def ToDict(self):
        """Chuyển dự án thành dictionary để lưu JSON."""
        return {
            "MaDuAn": self.maDuAn,
            "TenDuAn": self.tenDuAn,
            "DanhSachCot": self.danhSachCot,
            "ThanhVienThamGia": self.thanhVienThamGia,
            "DanhSachCongViec": [
                cong_viec.toDict() for cong_viec in self.danhSachCongViec
            ],
            "NgayTao": self.ngayTao,
        }

    @classmethod
    def FromDict(cls, data):
        """Tạo dự án và các object công việc từ dữ liệu JSON """
        if not isinstance(data, dict):
            print("Dữ liệu dự án phải là dictionary")
            return None

        from models.CongViec import CongViec

        du_lieu_cong_viec = data.get("DanhSachCongViec", [])
        if not isinstance(du_lieu_cong_viec, list):
            print("DanhSachCongViec trong JSON phải là list")
            return None

        return cls(
            maDuAn=data.get("MaDuAn"),
            tenDuAn=data.get("TenDuAn"),
            danhSachCot=data.get("DanhSachCot"),
            thanhVienThamGia=data.get("ThanhVienThamGia", []),
            danhSachCongViec=[
                CongViec.fromDict(cong_viec)
                for cong_viec in du_lieu_cong_viec
            ],
            ngayTao=data.get("NgayTao"),
        )


