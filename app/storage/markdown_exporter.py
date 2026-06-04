from pathlib import Path

from app.models.operation_log import OperationLog


class MarkdownExporter:
    def __init__(self, summaries_folder: str | Path = "data/summaries") -> None:
        self.summaries_folder = Path(summaries_folder)
        self.summaries_folder.mkdir(parents=True, exist_ok=True)

    def export(self, operation_log: OperationLog) -> Path:
        summary_path = self.summaries_folder / f"summary_{operation_log.operation_id}.md"
        content = self._build_content(operation_log)

        summary_path.write_text(content, encoding="utf-8")

        return summary_path

    def _build_content(self, operation_log: OperationLog) -> str:
        moved_count = len(operation_log.movements)

        lines = [
            "# Folder Organization Summary",
            "",
            "## Operation details",
            "",
            f"- Operation ID: `{operation_log.operation_id}`",
            f"- Created at: `{operation_log.created_at.strftime('%Y-%m-%d %H:%M:%S')}`",
            f"- Root folder: `{operation_log.root_folder}`",
            f"- Files moved: `{moved_count}`",
            "",
            "## Moved files",
            "",
        ]

        if not operation_log.movements:
            lines.append("No files were moved.")
            lines.append("")
            return "\n".join(lines)

        lines.extend(
            [
                "| File name | Category | Original path | New path |",
                "|---|---|---|---|",
            ]
        )

        for movement in operation_log.movements:
            lines.append(
                f"| {movement.file_name} | {movement.category} | "
                f"`{movement.source_path}` | `{movement.target_path}` |"
            )

        lines.extend(
            [
                "",
                "## Notes",
                "",
                "- Only files approved by the user were moved.",
                "- Files marked as skip were not touched.",
                "- Existing files were not overwritten.",
                "- This operation can be reverted using the latest operation log.",
                "",
            ]
        )

        return "\n".join(lines)