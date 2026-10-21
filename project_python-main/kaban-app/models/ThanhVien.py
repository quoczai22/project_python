"""
Proxy module tương thích ngược cho models.NguoiDung.
Các thành phần đã được tách thành package riêng: models/NguoiDung/
"""
from models.NguoiDung import NguoiDung, ThanhVien, QuanTriVien

__all__ = ["NguoiDung", "ThanhVien", "QuanTriVien"]
