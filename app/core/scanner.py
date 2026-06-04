from pathlib import Path

from app.models.file_item import FileItem


class FolderScanner:
    def scan(self, folder_path: str | Path) -> list[FileItem]:
        folder = Path(folder_path)

        if not folder.exists():
            raise FileNotFoundError(f"The folder does not exist: {folder}")

        if not folder.is_dir():
            raise NotADirectoryError(f"The path is not a folder: {folder}")

        files = []

        for item in folder.iterdir():
            if item.is_file():
                files.append(FileItem.from_path(item))

        return files