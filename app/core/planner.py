from pathlib import Path

from app.core.classifier import FileClassifier
from app.models.file_item import FileItem
from app.models.move_plan import MovePlan


class MovePlanner:
    def __init__(self, classifier: FileClassifier | None = None) -> None:
        self.classifier = classifier or FileClassifier()

    def create_plan(self, root_folder: str | Path, files: list[FileItem]) -> list[MovePlan]:
        root = Path(root_folder)
        plans = []

        for file_item in files:
            category, confidence, reason = self.classifier.classify(file_item)
            target_path = root / category / file_item.name

            plans.append(
                MovePlan(
                    file_item=file_item,
                    source_path=file_item.path,
                    target_path=target_path,
                    category=category,
                    confidence=confidence,
                    reason=reason,
                    approved=True,
                )
            )

        return plans