import json
from dataclasses import asdict
from datetime import datetime
from pathlib import Path

from app.models.operation_log import MovementLog, OperationLog


class LogRepository:
    def __init__(self, logs_folder: str | Path = "data/logs") -> None:
        self.logs_folder = Path(logs_folder)
        self.logs_folder.mkdir(parents=True, exist_ok=True)

    def save(self, operation_log: OperationLog) -> Path:
        log_path = self.logs_folder / f"{operation_log.operation_id}.json"

        data = {
            "operation_id": operation_log.operation_id,
            "created_at": operation_log.created_at.isoformat(),
            "root_folder": str(operation_log.root_folder),
            "movements": [
                {
                    "source_path": str(movement.source_path),
                    "target_path": str(movement.target_path),
                    "category": movement.category,
                    "file_name": movement.file_name,
                }
                for movement in operation_log.movements
            ],
        }

        log_path.write_text(
            json.dumps(data, indent=2, ensure_ascii=False),
            encoding="utf-8",
        )

        return log_path

    def get_latest_log_path(self) -> Path | None:
        log_files = sorted(
            self.logs_folder.glob("*.json"),
            key=lambda path: path.stat().st_mtime,
            reverse=True,
        )

        if not log_files:
            return None

        return log_files[0]

    def load_latest(self) -> OperationLog | None:
        latest_log_path = self.get_latest_log_path()

        if latest_log_path is None:
            return None

        data = json.loads(latest_log_path.read_text(encoding="utf-8"))

        movements = [
            MovementLog(
                source_path=Path(item["source_path"]),
                target_path=Path(item["target_path"]),
                category=item["category"],
                file_name=item["file_name"],
            )
            for item in data["movements"]
        ]

        return OperationLog(
            operation_id=data["operation_id"],
            created_at=datetime.fromisoformat(data["created_at"]),
            root_folder=Path(data["root_folder"]),
            movements=movements,
        )