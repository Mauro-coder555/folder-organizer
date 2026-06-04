from dataclasses import dataclass
from pathlib import Path
from datetime import datetime


@dataclass
class FileItem:
    path: Path
    name: str
    extension: str
    size_bytes: int
    created_at: datetime
    modified_at: datetime

    @classmethod
    def from_path(cls, file_path: Path) -> "FileItem":
        stats = file_path.stat()

        return cls(
            path=file_path,
            name=file_path.name,
            extension=file_path.suffix.lower(),
            size_bytes=stats.st_size,
            created_at=datetime.fromtimestamp(stats.st_ctime),
            modified_at=datetime.fromtimestamp(stats.st_mtime),
        )