from dataclasses import dataclass
from pathlib import Path

from app.models.file_item import FileItem


@dataclass
class MovePlan:
    file_item: FileItem
    source_path: Path
    target_path: Path
    category: str
    confidence: str
    reason: str
    approved: bool = True