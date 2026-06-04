from app.config.rules import (
    ARCHIVE_EXTENSIONS,
    CONTRACT_KEYWORDS,
    DOCUMENT_EXTENSIONS,
    IMAGE_EXTENSIONS,
    INVOICE_KEYWORDS,
    REPORT_KEYWORDS,
    SCREENSHOT_KEYWORDS,
    SPREADSHEET_EXTENSIONS,
    VIDEO_EXTENSIONS,
)
from app.models.file_item import FileItem


class FileClassifier:
    def classify(self, file_item: FileItem) -> tuple[str, str, str]:
        normalized_name = file_item.name.lower()
        extension = file_item.extension.lower()

        if self._contains_any_keyword(normalized_name, SCREENSHOT_KEYWORDS):
            return "screenshots", "high", "File name looks like a screenshot"

        if self._contains_any_keyword(normalized_name, INVOICE_KEYWORDS):
            return "invoices", "high", "File name contains invoice-related keywords"

        if self._contains_any_keyword(normalized_name, CONTRACT_KEYWORDS):
            return "contracts", "high", "File name contains contract-related keywords"

        if self._contains_any_keyword(normalized_name, REPORT_KEYWORDS):
            return "reports", "high", "File name contains report-related keywords"

        if extension in IMAGE_EXTENSIONS:
            return "images", "medium", "File extension is an image type"

        if extension in VIDEO_EXTENSIONS:
            return "videos", "medium", "File extension is a video type"

        if extension in SPREADSHEET_EXTENSIONS:
            return "spreadsheets", "medium", "File extension is a spreadsheet type"

        if extension in ARCHIVE_EXTENSIONS:
            return "archives", "medium", "File extension is an archive type"

        if extension in DOCUMENT_EXTENSIONS:
            return "documents", "medium", "File extension is a document type"

        return "others", "low", "No clear classification rule matched"

    def _contains_any_keyword(self, text: str, keywords: set[str]) -> bool:
        return any(keyword in text for keyword in keywords)