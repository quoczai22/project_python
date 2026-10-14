import json
import os
from .BoLuuTruBase import BoLuuTruBase
from models.ThanhVien import NguoiDung
from exceptions import LoiLuuTruError
from logger import logger


class BoLuuTruMock(BoLuuTruBase):
    """
    TÍNH KẾ THỪA (Inheritance) & ĐÓNG GÓI (Encapsulation):
    - Kế thừa từ BoLuuTruBase và triển khai thao tác file JSON.
    - Xử lý và chuyển tiếp ngoại lệ I/O thành LoiLuuTruError chuẩn hóa.
    """

    def __init__(self, ten_file_du_an="du_an.json", ten_file_du_lieu_moc="du_lieu_moc.json"):
        self.ten_file_du_an = ten_file_du_an or "du_an.json"
        self.ten_file_du_lieu_moc = ten_file_du_lieu_moc or "du_lieu_moc.json"
        self.ten_file_nhat_ky = "nhat_ky.json"

    def _lay_duong_dan(self, ten_file: str) -> str:
        if os.path.isabs(ten_file) or os.path.exists(ten_file):
            return ten_file
        # Đi lên 2 cấp thư mục: services/BoLuuTru -> services -> root
        base_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
        app_path = os.path.join(base_dir, ten_file)
        if os.path.exists(app_path):
            return app_path
        return ten_file

    def doc_json(self, ten_file: str):
        duong_dan = self._lay_duong_dan(ten_file)
        if not os.path.exists(duong_dan):
            raise LoiLuuTruError(f"Không tìm thấy file lưu trữ: {ten_file}", ten_nguon=ten_file)
        try:
            with open(duong_dan, "r", encoding="utf-8") as f:
                return json.load(f)
        except json.JSONDecodeError as err:
            raise LoiLuuTruError(f"File JSON '{ten_file}' bị hỏng cú pháp: {err}", ten_nguon=ten_file, loi_goc=err)
        except OSError as err:
            raise LoiLuuTruError(f"Lỗi khi đọc file '{ten_file}': {err}", ten_nguon=ten_file, loi_goc=err)

    def ghi_json(self, ten_file: str, du_lieu):
        duong_dan = self._lay_duong_dan(ten_file)
        try:
            with open(duong_dan, "w", encoding="utf-8") as f:
                json.dump(du_lieu, f, ensure_ascii=False, indent=2)
        except (OSError, TypeError) as err:
            raise LoiLuuTruError(f"Không thể ghi dữ liệu vào file '{ten_file}': {err}", ten_nguon=ten_file, loi_goc=err)

    def ghi_nhat_ky(self, du_lieu_log: dict):
        duong_dan = self._lay_duong_dan(self.ten_file_nhat_ky)
        danh_sach = []
        if os.path.exists(duong_dan):
            try:
                with open(duong_dan, "r", encoding="utf-8") as f:
                    danh_sach = json.load(f)
            except Exception:
                danh_sach = []
        danh_sach.append(du_lieu_log)
        try:
            with open(duong_dan, "w", encoding="utf-8") as f:
                json.dump(danh_sach, f, ensure_ascii=False, indent=2)
        except OSError as err:
            logger.error(f"Lỗi ghi nhật ký hệ thống: {err}")

    def doc_danh_sach_thanh_vien(self):
        """Khởi tạo danh sách đối tượng người dùng đa hình (QuanTriVien hoặc ThanhVien)."""
        try:
            du_lieu = self.doc_json(self.ten_file_du_lieu_moc)
        except LoiLuuTruError:
            logger.warning("Không thể đọc file dữ liệu mốc người dùng, sử dụng danh sách rỗng")
            du_lieu = {}

        if isinstance(du_lieu, dict):
            ds = du_lieu.get("thanh_vien", [])
        elif isinstance(du_lieu, list):
            ds = du_lieu
        else:
            ds = []

        danh_sach = []
        for item in ds:
            if isinstance(item, dict):
                nguoi_dung = NguoiDung.from_dict(item)
                if nguoi_dung:
                    danh_sach.append(nguoi_dung)
        return danh_sach
