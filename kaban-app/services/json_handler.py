"""services.json_handler: Đọc và ghi dữ liệu JSON an toàn kèm cơ chế sao lưu."""
import os
import json
from services.BoLuuTru.BoLuuTruMock import BoLuuTruMock


class JsonHandler(BoLuuTruMock):
    """
    Xử lý lưu trữ JSON:
    - Đọc (json.load) và ghi (json.dump) dữ liệu với mã hóa UTF-8.
    - Tự động sao lưu và khôi phục khi file gặp sự cố.
    """

    def __init__(self, ten_file_du_an: str = None, ten_file_du_lieu_moc: str = None):
        super().__init__(ten_file_du_an=ten_file_du_an, ten_file_du_lieu_moc=ten_file_du_lieu_moc)

    def doc_du_lieu(self, ten_file: str) -> dict:
        return self.doc_json(ten_file)

    def ghi_du_lieu(self, ten_file: str, du_lieu) -> bool:
        return self.ghi_json(ten_file, du_lieu)


def doc_file_json(duong_dan: str) -> dict:
    """Hàm helper đọc file JSON nhanh."""
    if not os.path.exists(duong_dan):
        return {}
    with open(duong_dan, "r", encoding="utf-8") as f:
        return json.load(f)


def ghi_file_json(duong_dan: str, du_lieu) -> None:
    """Hàm helper ghi file JSON nhanh."""
    os.makedirs(os.path.dirname(os.path.abspath(duong_dan)), exist_ok=True)
    with open(duong_dan, "w", encoding="utf-8") as f:
        json.dump(du_lieu, f, ensure_ascii=False, indent=2)
