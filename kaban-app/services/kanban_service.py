"""services.kanban_service: Dịch vụ nghiệp vụ quản lý bảng Kanban."""
from services.QuanLyKaban import QuanLyKanban

# Alias tương thích kiến trúc chuẩn
KanbanService = QuanLyKanban

__all__ = [
    "QuanLyKanban",
    "KanbanService",
]
