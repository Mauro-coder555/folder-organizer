from dataclasses import dataclass
from datetime import datetime
from pathlib import Path


@dataclass
class MovementLog:
    source_path: Path
    target_path: Path
    category: str
    file_name: str


@dataclass
class OperationLog:
    operation_id: str
    created_at: datetime
    root_folder: Path
    movements: list[MovementLog]