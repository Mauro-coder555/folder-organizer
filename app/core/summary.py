from pathlib import Path

from app.models.operation_log import OperationLog
from app.storage.markdown_exporter import MarkdownExporter


class SummaryService:
    def __init__(self, markdown_exporter: MarkdownExporter | None = None) -> None:
        self.markdown_exporter = markdown_exporter or MarkdownExporter()

    def export_operation_summary(self, operation_log: OperationLog) -> Path:
        return self.markdown_exporter.export(operation_log)