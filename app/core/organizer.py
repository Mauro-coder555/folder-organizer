import shutil
from datetime import datetime
from pathlib import Path
from uuid import uuid4

from app.models.move_plan import MovePlan
from app.models.operation_log import MovementLog, OperationLog
from app.storage.log_repository import LogRepository


class FolderOrganizer:
    def __init__(self, log_repository: LogRepository | None = None) -> None:
        self.log_repository = log_repository or LogRepository()

    def apply(self, root_folder: str | Path, plans: list[MovePlan]) -> OperationLog:
        approved_plans = [plan for plan in plans if plan.approved]

        operation_log = OperationLog(
            operation_id=self._create_operation_id(),
            created_at=datetime.now(),
            root_folder=Path(root_folder),
            movements=[],
        )

        for plan in approved_plans:
            source_path = plan.source_path
            target_path = plan.target_path

            if not source_path.exists():
                continue

            safe_target_path = self._get_available_target_path(target_path)
            safe_target_path.parent.mkdir(parents=True, exist_ok=True)

            shutil.move(str(source_path), str(safe_target_path))

            operation_log.movements.append(
                MovementLog(
                    source_path=source_path,
                    target_path=safe_target_path,
                    category=plan.category,
                    file_name=source_path.name,
                )
            )

        self.log_repository.save(operation_log)

        return operation_log

    def _get_available_target_path(self, target_path: Path) -> Path:
        if not target_path.exists():
            return target_path

        stem = target_path.stem
        suffix = target_path.suffix
        parent = target_path.parent

        counter = 1

        while True:
            candidate = parent / f"{stem}_{counter}{suffix}"

            if not candidate.exists():
                return candidate

            counter += 1

    def _create_operation_id(self) -> str:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        short_id = uuid4().hex[:8]
        return f"operation_{timestamp}_{short_id}"