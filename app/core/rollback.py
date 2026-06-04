import shutil
from pathlib import Path

from app.models.operation_log import OperationLog
from app.storage.log_repository import LogRepository


class RollbackManager:
    def __init__(self, log_repository: LogRepository | None = None) -> None:
        self.log_repository = log_repository or LogRepository()

    def undo_last_operation(self) -> int:
        operation_log = self.log_repository.load_latest()

        if operation_log is None:
            return 0

        return self.undo(operation_log)

    def undo(self, operation_log: OperationLog) -> int:
        restored_count = 0

        for movement in reversed(operation_log.movements):
            current_path = movement.target_path
            original_path = movement.source_path

            if not current_path.exists():
                continue

            safe_original_path = self._get_available_path(original_path)
            safe_original_path.parent.mkdir(parents=True, exist_ok=True)

            shutil.move(str(current_path), str(safe_original_path))
            restored_count += 1

        return restored_count

    def _get_available_path(self, path: Path) -> Path:
        if not path.exists():
            return path

        stem = path.stem
        suffix = path.suffix
        parent = path.parent

        counter = 1

        while True:
            candidate = parent / f"{stem}_restored_{counter}{suffix}"

            if not candidate.exists():
                return candidate

            counter += 1