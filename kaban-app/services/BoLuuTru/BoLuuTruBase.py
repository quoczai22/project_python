from abc import ABC, abstractmethod


class BoLuuTruBase(ABC):
    """
    Lớp cơ sở trừu tượng (Abstract Base Class) cho tầng lưu trữ dữ liệu.
    
    TÍNH TRỪU TƯỢNG (Abstraction):
    - Định nghĩa giao diện lưu trữ chuẩn hóa cho ứng dụng Kanban.
    - Áp dụng nguyên lý Dependency Inversion (DIP): Service phụ thuộc vào Abstraction, 
      không phụ thuộc vào cài đặt cụ thể (File JSON, Database, Cloud API,...).
    """

    @abstractmethod
    def doc_json(self, ten_file: str):
        """Đọc dữ liệu từ nguồn lưu trữ định dạng JSON."""
        pass

    @abstractmethod
    def ghi_json(self, ten_file: str, du_lieu):
        """Ghi dữ liệu ra nguồn lưu trữ định dạng JSON."""
        pass

    @abstractmethod
    def sao_luu(self, ten_file: str):
        """Sao lưu bản hợp lệ hiện tại của một nguồn dữ liệu; trả về đường dẫn bản sao lưu (hoặc None)."""
        pass

    @abstractmethod
    def ghi_nhat_ky(self, du_lieu_log: dict):
        """Ghi nhật ký lịch sử hoạt động hệ thống."""
        pass

    @abstractmethod
    def doc_nhat_ky(self):
        """Đọc toàn bộ nhật ký (danh sách dict theo thứ tự thời gian)."""
        pass

    @abstractmethod
    def doc_danh_sach_thanh_vien(self):
        """Đọc danh sách người dùng từ nguồn dữ liệu."""
        pass

    @abstractmethod
    def ghi_danh_sach_thanh_vien(self, danh_sach):
        """Ghi toàn bộ danh sách người dùng xuống nguồn dữ liệu."""
        pass
