import json
import os
import re
import sys
import tempfile
from datetime import datetime

from .BoLuuTruBase import BoLuuTruBase
from models.ThanhVien import NguoiDung
from models.NguoiDung.NguoiDungBase import bam_mat_khau, la_mat_khau_da_bam
from config import (
    TEN_FILE_DU_AN, TEN_FILE_DU_LIEU_MOC, TEN_FILE_NHAT_KY,
    TEN_THU_MUC_SAO_LUU, SO_BAN_SAO_LUU_TOI_DA
)
from exceptions import KanbanException, LoiLuuTruError
from logger import logger

# Tài khoản mẫu khi chưa có file người dùng: đúng 1 quản trị + 1 thành viên.
# Mật khẩu ở đây là mật khẩu thô, sẽ được băm SHA-256 khi tạo đối tượng NguoiDung.
TAI_KHOAN_MAU = (
    {"ten_dang_nhap": "admin", "mat_khau": "123456", "ho_ten": "Quản trị viên Hệ thống",
     "email": "admin@kanban.vn", "vai_tro": "quan_tri"},
    {"ten_dang_nhap": "khoa", "mat_khau": "123456", "ho_ten": "Đăng Khoa",
     "email": "khoa@kanban.vn", "vai_tro": "thanh_vien"},
)


class _FileHong(Exception):
    """Nội bộ: file tồn tại nhưng nội dung rỗng / sai cú pháp / sai định dạng (có thể khôi phục từ backup)."""


class BoLuuTruMock(BoLuuTruBase):
    """
    TÍNH KẾ THỪA (Inheritance) & ĐÓNG GÓI (Encapsulation):
    - Kế thừa từ BoLuuTruBase và triển khai thao tác file JSON.
    - Xử lý và chuyển tiếp ngoại lệ I/O thành LoiLuuTruError chuẩn hóa.

    Cơ chế an toàn dữ liệu:
    - Ghi nguyên tử: ghi ra file .tmp rồi os.replace -> mất điện/lỗi giữa chừng không làm hỏng file gốc.
    - Sao lưu tự động trước mỗi lần ghi đè (thư mục backup/, giữ SO_BAN_SAO_LUU_TOI_DA bản mới nhất).
    - Khi đọc gặp file thiếu/rỗng/hỏng/sai định dạng: tự khôi phục từ bản sao lưu hợp lệ mới nhất.
    - File hỏng không bao giờ bị ghi đè mất: luôn được giữ lại dạng '<tên>.loi-<thời gian>'.
    """

    def __init__(self, ten_file_du_an=None, ten_file_du_lieu_moc=None):
        self.ten_file_du_an = ten_file_du_an or TEN_FILE_DU_AN
        self.ten_file_du_lieu_moc = ten_file_du_lieu_moc or TEN_FILE_DU_LIEU_MOC
        self.ten_file_nhat_ky = TEN_FILE_NHAT_KY

    # ==================== ĐƯỜNG DẪN ====================
    def _lay_duong_dan(self, ten_file: str) -> str:
        if os.path.isabs(ten_file):
            return ten_file
        if getattr(sys, "frozen", False):
            # Chạy từ file .exe (PyInstaller): dữ liệu nằm cạnh file .exe, không phải thư mục tạm.
            base_dir = os.path.dirname(os.path.abspath(sys.executable))
        else:
            # services/BoLuuTru -> services -> thư mục gốc kaban-app
            base_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
        return os.path.join(base_dir, ten_file)

    @staticmethod
    def _thu_muc_sao_luu(duong_dan: str) -> str:
        return os.path.join(os.path.dirname(duong_dan), TEN_THU_MUC_SAO_LUU)

    def _kieu_mong_doi(self, duong_dan: str):
        """Kiểu dữ liệu JSON gốc mà từng file bắt buộc phải có (None = không kiểm tra)."""
        ten = os.path.basename(duong_dan)
        if ten == os.path.basename(self.ten_file_du_an):
            return list
        if ten == os.path.basename(self.ten_file_du_lieu_moc):
            return (dict, list)
        if ten == os.path.basename(self.ten_file_nhat_ky):
            return list
        return None

    # ==================== ĐỌC / GHI THÔ ====================
    def _la_file_tai_khoan(self, ten_file: str) -> bool:
        return os.path.basename(ten_file) == os.path.basename(self.ten_file_du_lieu_moc)

    def _bam_mat_khau_tho(self, ten_file: str, du_lieu):
        """Chuẩn hóa tài khoản cũ trước khi ghi dữ liệu chính hoặc bản sao lưu."""
        if not self._la_file_tai_khoan(ten_file):
            return du_lieu
        cac_tai_khoan = du_lieu.get("thanh_vien") if isinstance(du_lieu, dict) else du_lieu
        if not isinstance(cac_tai_khoan, list):
            return du_lieu
        can_bam = {}
        for i, tai_khoan in enumerate(cac_tai_khoan):
            if isinstance(tai_khoan, dict):
                mat_khau = tai_khoan.get("mat_khau")
                if mat_khau is not None and mat_khau != "" and not la_mat_khau_da_bam(mat_khau):
                    can_bam[i] = dict(tai_khoan, mat_khau=bam_mat_khau(mat_khau))
        if not can_bam:
            return du_lieu
        danh_sach = [can_bam.get(i, tai_khoan) for i, tai_khoan in enumerate(cac_tai_khoan)]
        if isinstance(du_lieu, dict):
            return dict(du_lieu, thanh_vien=danh_sach)
        return danh_sach

    def _doc_file(self, duong_dan: str, ten_file: str):
        """
        Trả về (dữ liệu JSON, nội dung bytes) đã đọc từ cùng một lần mở file.
        - Ném LoiLuuTruError nếu lỗi I/O (quyền truy cập, ổ đĩa...).
        - Ném _FileHong nếu nội dung rỗng / sai cú pháp / sai mã hóa / sai kiểu dữ liệu.
        """
        try:
            with open(duong_dan, "rb") as f:
                noi_dung_byte = f.read()
            noi_dung = noi_dung_byte.decode("utf-8-sig")
        except FileNotFoundError:
            raise
        except UnicodeDecodeError as err:
            raise _FileHong(f"không phải văn bản UTF-8 hợp lệ ({err})")
        except OSError as err:
            raise LoiLuuTruError(f"Lỗi khi đọc file '{ten_file}': {err}", ten_nguon=ten_file, loi_goc=err)

        if not noi_dung.strip():
            raise _FileHong("bị rỗng")
        try:
            du_lieu = json.loads(noi_dung)
        except json.JSONDecodeError as err:
            raise _FileHong(f"bị hỏng cú pháp JSON: {err}")

        kieu = self._kieu_mong_doi(ten_file)
        if kieu is not None and not isinstance(du_lieu, kieu):
            ten_kieu = " hoặc ".join(k.__name__ for k in (kieu if isinstance(kieu, tuple) else (kieu,)))
            raise _FileHong(f"sai định dạng: cần {ten_kieu} nhưng gặp {type(du_lieu).__name__}")
        if self._la_file_tai_khoan(ten_file) and isinstance(du_lieu, dict):
            if not isinstance(du_lieu.get("thanh_vien"), list):
                raise _FileHong("sai định dạng: 'thanh_vien' phải là danh sách")
        return du_lieu, noi_dung_byte

    @staticmethod
    def _ghi_nguyen_tu(duong_dan: str, noi_dung):
        """Ghi file an toàn: ghi ra .tmp rồi thay thế file gốc bằng os.replace."""
        thu_muc = os.path.dirname(duong_dan)
        if thu_muc:
            os.makedirs(thu_muc, exist_ok=True)
        du_lieu_byte = noi_dung if isinstance(noi_dung, bytes) else noi_dung.encode("utf-8")
        duong_dan_tam = None
        try:
            with tempfile.NamedTemporaryFile(mode="wb", dir=thu_muc or ".", suffix=".tmp", delete=False) as f:
                duong_dan_tam = f.name
                f.write(du_lieu_byte)
                f.flush()
                os.fsync(f.fileno())
            os.replace(duong_dan_tam, duong_dan)
        except BaseException:
            if duong_dan_tam is not None:
                try:
                    os.remove(duong_dan_tam)
                except OSError:
                    pass
            raise

    # ==================== SAO LƯU / KHÔI PHỤC ====================
    @staticmethod
    def _mau_ten_sao_luu(duong_dan: str):
        goc, duoi = os.path.splitext(os.path.basename(duong_dan))
        return goc, duoi

    def _liet_ke_sao_luu(self, duong_dan: str):
        """Các bản sao lưu của file, MỚI NHẤT trước."""
        thu_muc = self._thu_muc_sao_luu(duong_dan)
        try:
            cac_tep = os.listdir(thu_muc)
        except FileNotFoundError:
            return []
        goc, duoi = self._mau_ten_sao_luu(duong_dan)
        mau = re.compile(rf"{re.escape(goc)}_\d{{8}}_\d{{6}}_\d{{6}}{re.escape(duoi)}")
        ten_ban = sorted((t for t in cac_tep if mau.fullmatch(t)), reverse=True)
        return [os.path.join(thu_muc, t) for t in ten_ban]

    def danh_sach_sao_luu(self, ten_file: str):
        """Danh sách đường dẫn các bản sao lưu của một file (mới nhất trước)."""
        try:
            return self._liet_ke_sao_luu(self._lay_duong_dan(ten_file))
        except OSError as err:
            raise LoiLuuTruError(f"Không thể liệt kê bản sao lưu của '{ten_file}'", ten_nguon=ten_file, loi_goc=err)

    def _giu_file_hong(self, duong_dan: str):
        """Cất bản sao của file hỏng sang backup/ để không bị ghi đè mất."""
        try:
            with open(duong_dan, "rb") as f:
                noi_dung = f.read()
        except FileNotFoundError:
            return
        thu_muc = self._thu_muc_sao_luu(duong_dan)
        ten = os.path.basename(duong_dan)
        dau_thoi_gian = datetime.now().strftime("%Y%m%d_%H%M%S_%f")
        dich = os.path.join(thu_muc, f"{ten}.loi-{dau_thoi_gian}")
        self._ghi_nguyen_tu(dich, noi_dung)
        logger.warning(f"Đã giữ lại bản file hỏng tại: {dich}")
        cu = sorted(t for t in os.listdir(thu_muc) if t.startswith(ten + ".loi-"))
        for t in cu[:-5]:
            os.remove(os.path.join(thu_muc, t))

    def sao_luu(self, ten_file: str):
        """
        Sao lưu bản HỢP LỆ hiện tại của file vào backup/<tên>_<thời gian>.json.
        - File chưa tồn tại: trả về None.
        - File đang hỏng: không sao lưu (tránh đẩy bản tốt ra khỏi danh sách), chỉ giữ lại bản hỏng.
        - Nội dung giống hệt bản sao lưu mới nhất: không tạo thêm bản trùng.
        """
        duong_dan = self._lay_duong_dan(ten_file)
        try:
            try:
                du_lieu, noi_dung = self._doc_file(duong_dan, ten_file)
            except FileNotFoundError:
                return None
            except _FileHong as loi:
                logger.warning(f"Không sao lưu '{ten_file}' vì file {loi}")
                self._giu_file_hong(duong_dan)
                return None

            du_lieu_an_toan = self._bam_mat_khau_tho(ten_file, du_lieu)
            if du_lieu_an_toan is not du_lieu:
                noi_dung = json.dumps(du_lieu_an_toan, ensure_ascii=False, indent=2).encode("utf-8")
            for ban in self._liet_ke_sao_luu(duong_dan)[:1]:
                with open(ban, "rb") as f:
                    if f.read() == noi_dung:
                        return ban

            thu_muc = self._thu_muc_sao_luu(duong_dan)
            os.makedirs(thu_muc, exist_ok=True)
            goc, duoi = self._mau_ten_sao_luu(duong_dan)
            dich = os.path.join(thu_muc, f"{goc}_{datetime.now().strftime('%Y%m%d_%H%M%S_%f')}{duoi}")
            self._ghi_nguyen_tu(dich, noi_dung)

            for ban_cu in self._liet_ke_sao_luu(duong_dan)[SO_BAN_SAO_LUU_TOI_DA:]:
                os.remove(ban_cu)
            return dich
        except OSError as err:
            raise LoiLuuTruError(f"Không thể sao lưu file '{ten_file}': {err}", ten_nguon=ten_file, loi_goc=err)

    def _khoi_phuc_tu_sao_luu(self, duong_dan: str, ten_file: str):
        """Thử khôi phục file từ bản sao lưu hợp lệ mới nhất. Trả về (thanh_cong, du_lieu)."""
        for ban in self.danh_sach_sao_luu(ten_file):
            try:
                du_lieu, noi_dung = self._doc_file(ban, ten_file)
            except (_FileHong, FileNotFoundError):
                continue
            try:
                self._giu_file_hong(duong_dan)
                du_lieu_an_toan = self._bam_mat_khau_tho(ten_file, du_lieu)
                if du_lieu_an_toan is not du_lieu:
                    noi_dung = json.dumps(du_lieu_an_toan, ensure_ascii=False, indent=2)
                self._ghi_nguyen_tu(duong_dan, noi_dung)
            except OSError as err:
                raise LoiLuuTruError(f"Không thể khôi phục file '{ten_file}'", ten_nguon=ten_file, loi_goc=err)
            logger.warning(f"Đã khôi phục '{ten_file}' từ bản sao lưu: {os.path.basename(ban)}")
            return True, du_lieu_an_toan
        return False, None

    # ==================== API CHUẨN ====================
    def doc_json(self, ten_file: str):
        duong_dan = self._lay_duong_dan(ten_file)
        try:
            du_lieu, _ = self._doc_file(duong_dan, ten_file)
            return du_lieu
        except FileNotFoundError:
            thanh_cong, du_lieu = self._khoi_phuc_tu_sao_luu(duong_dan, ten_file)
            if thanh_cong:
                return du_lieu
            loi = LoiLuuTruError(f"Không tìm thấy file lưu trữ: {ten_file}", ten_nguon=ten_file)
            loi.chi_tiet["nguyen_nhan"] = "file_thieu"
            raise loi
        except _FileHong as loi:
            logger.error(f"File '{ten_file}' {loi}; đang thử khôi phục từ bản sao lưu")
            thanh_cong, du_lieu = self._khoi_phuc_tu_sao_luu(duong_dan, ten_file)
            if thanh_cong:
                return du_lieu
            ngoai_le = LoiLuuTruError(
                f"File '{ten_file}' {loi} và không có bản sao lưu hợp lệ để khôi phục",
                ten_nguon=ten_file, loi_goc=loi
            )
            ngoai_le.chi_tiet["nguyen_nhan"] = "file_hong"
            raise ngoai_le

    def ghi_json(self, ten_file: str, du_lieu):
        duong_dan = self._lay_duong_dan(ten_file)
        try:
            du_lieu_an_toan = self._bam_mat_khau_tho(ten_file, du_lieu)
            noi_dung = json.dumps(du_lieu_an_toan, ensure_ascii=False, indent=2).encode("utf-8")
        except (TypeError, ValueError) as err:
            raise LoiLuuTruError(f"Dữ liệu không thể chuyển sang JSON để ghi vào '{ten_file}': {err}",
                                 ten_nguon=ten_file, loi_goc=err)
        self.sao_luu(ten_file)
        try:
            self._ghi_nguyen_tu(duong_dan, noi_dung)
        except OSError as err:
            raise LoiLuuTruError(f"Không thể ghi dữ liệu vào file '{ten_file}': {err}",
                                 ten_nguon=ten_file, loi_goc=err)

    # ==================== NHẬT KÝ ====================
    def ghi_nhat_ky(self, du_lieu_log: dict):
        """Thêm 1 bản ghi vào nhat_ky.json. Không ném lỗi: thất bại chỉ ghi log và trả về False."""
        if not isinstance(du_lieu_log, dict):
            logger.error("Bản ghi nhật ký phải là dict")
            return False
        ban_ghi = dict(du_lieu_log)
        ban_ghi.setdefault("thoi_gian", datetime.now().isoformat())

        try:
            danh_sach = self.doc_json(self.ten_file_nhat_ky)
        except LoiLuuTruError as err:
            if err.chi_tiet.get("nguyen_nhan") not in ("file_thieu", "file_hong"):
                logger.error(f"Không đọc được nhật ký, bỏ qua bản ghi mới: {err.thong_diep}")
                return False
            danh_sach = []
        danh_sach.append(ban_ghi)

        try:
            self.ghi_json(self.ten_file_nhat_ky, danh_sach)
            return True
        except LoiLuuTruError as err:
            logger.error(f"Lỗi ghi nhật ký hệ thống: {err.thong_diep}")
            return False

    def doc_nhat_ky(self):
        """Đọc nhật ký theo thứ tự thời gian (cũ -> mới). Lỗi hoặc chưa có file -> danh sách rỗng."""
        try:
            du_lieu = self.doc_json(self.ten_file_nhat_ky)
        except LoiLuuTruError as err:
            if err.chi_tiet.get("nguyen_nhan") != "file_thieu":
                logger.error(f"Không đọc được nhật ký: {err.thong_diep}")
            return []
        return [muc for muc in du_lieu if isinstance(muc, dict)]

    # ==================== NGƯỜI DÙNG ====================
    def ghi_danh_sach_thanh_vien(self, danh_sach):
        """Ghi toàn bộ tài khoản (đối tượng NguoiDung hoặc dict) xuống file người dùng."""
        muc = [nd.to_dict() if hasattr(nd, "to_dict") else nd for nd in danh_sach]
        self.ghi_json(self.ten_file_du_lieu_moc, {"thanh_vien": muc})

    def khoi_tao_du_lieu_mau(self):
        """Tạo file người dùng mẫu (1 quan_tri + 1 thanh_vien) và trả về danh sách đối tượng."""
        danh_sach = [NguoiDung.from_dict(dict(tk)) for tk in TAI_KHOAN_MAU]
        self.ghi_danh_sach_thanh_vien(danh_sach)
        logger.warning(f"Đã tạo dữ liệu mẫu '{self.ten_file_du_lieu_moc}': "
                       f"{', '.join(nd.ten_dang_nhap for nd in danh_sach)}")
        return danh_sach

    def doc_danh_sach_thanh_vien(self):
        """
        Khởi tạo danh sách đối tượng người dùng đa hình (QuanTriVien hoặc ThanhVien).
        - Bản ghi lỗi bị bỏ qua (có ghi log), không làm sập đăng nhập của người khác.
        - Mật khẩu thô còn sót trong file cũ được tự động băm và ghi lại.
        - File chưa có / hỏng không khôi phục được / không có tài khoản hợp lệ: tạo dữ liệu mẫu.
        """
        try:
            du_lieu = self.doc_json(self.ten_file_du_lieu_moc)
        except LoiLuuTruError as err:
            nguyen_nhan = err.chi_tiet.get("nguyen_nhan")
            if nguyen_nhan not in ("file_thieu", "file_hong"):
                logger.warning(f"Không đọc được file người dùng: {err.thong_diep}")
                return []
            if nguyen_nhan == "file_hong":
                logger.warning(err.thong_diep)
            du_lieu = None

        ds_tho = []
        if isinstance(du_lieu, dict):
            ds_tho = du_lieu.get("thanh_vien", [])
        elif isinstance(du_lieu, list):
            ds_tho = du_lieu
        if not isinstance(ds_tho, list):
            ds_tho = []

        danh_sach = []
        can_ghi_lai = False
        for item in ds_tho:
            if not isinstance(item, dict):
                logger.warning("Bỏ qua bản ghi người dùng không phải dict")
                continue
            try:
                nguoi_dung = NguoiDung.from_dict(item)
            except KanbanException as err:
                logger.warning(f"Bỏ qua tài khoản lỗi {item.get('ten_dang_nhap')!r}: {err.thong_diep}")
                continue
            danh_sach.append(nguoi_dung)
            if not la_mat_khau_da_bam(item.get("mat_khau")):
                item["mat_khau"] = nguoi_dung.to_dict()["mat_khau"]  # nâng cấp mật khẩu thô -> đã băm
                can_ghi_lai = True

        if not danh_sach:
            logger.warning("Không có tài khoản hợp lệ nào, tạo tài khoản mẫu")
            try:
                return self.khoi_tao_du_lieu_mau()
            except Exception as err:
                logger.error(f"Không tạo được dữ liệu mẫu: {err}")
                return []

        if can_ghi_lai:
            try:
                self.ghi_json(self.ten_file_du_lieu_moc, du_lieu)
                logger.info("Đã băm SHA-256 các mật khẩu thô còn lại trong file người dùng")
            except Exception as err:
                logger.error(f"Không ghi lại được mật khẩu đã băm: {err}")
        return danh_sach
