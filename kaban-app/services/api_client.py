"""services.api_client: (Tùy chọn) Giao tiếp với REST API từ xa khi cần tích hợp mạng."""
import json
import urllib.request
import urllib.error


class ApiClient:
    """Client gửi request HTTP/REST API đơn giản bằng thư viện tiêu chuẩn."""

    def __init__(self, base_url: str = ""):
        self.base_url = base_url.rstrip("/")

    def get(self, endpoint: str, timeout: int = 10) -> dict:
        url = f"{self.base_url}/{endpoint.lstrip('/')}"
        try:
            req = urllib.request.Request(url, headers={"User-Agent": "KanbanApp/1.0"})
            with urllib.request.urlopen(req, timeout=timeout) as res:
                return json.loads(res.read().decode("utf-8"))
        except Exception:
            return {}

    def post(self, endpoint: str, data: dict, timeout: int = 10) -> dict:
        url = f"{self.base_url}/{endpoint.lstrip('/')}"
        try:
            json_data = json.dumps(data).encode("utf-8")
            req = urllib.request.Request(
                url, data=json_data,
                headers={"Content-Type": "application/json", "User-Agent": "KanbanApp/1.0"}
            )
            with urllib.request.urlopen(req, timeout=timeout) as res:
                return json.loads(res.read().decode("utf-8"))
        except Exception:
            return {}
