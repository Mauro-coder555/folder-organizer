import tempfile
import unittest
from pathlib import Path

from app.core.classifier import FileClassifier
from app.core.planner import MovePlanner
from app.core.scanner import FolderScanner


class TestFolderScanner(unittest.TestCase):
    def test_scan_returns_files_from_folder(self):
        with tempfile.TemporaryDirectory() as temporary_folder:
            folder = Path(temporary_folder)

            invoice_file = folder / "invoice_january.pdf"
            notes_file = folder / "notes.txt"
            nested_folder = folder / "nested"

            invoice_file.write_text("Fake invoice content", encoding="utf-8")
            notes_file.write_text("Some notes", encoding="utf-8")
            nested_folder.mkdir()

            scanner = FolderScanner()
            files = scanner.scan(folder)

            file_names = [file.name for file in files]

            self.assertEqual(len(files), 2)
            self.assertIn("invoice_january.pdf", file_names)
            self.assertIn("notes.txt", file_names)

    def test_scan_raises_error_when_folder_does_not_exist(self):
        scanner = FolderScanner()

        with self.assertRaises(FileNotFoundError):
            scanner.scan("folder_that_does_not_exist")


class TestFileClassifier(unittest.TestCase):
    def test_classifies_invoice_by_name(self):
        with tempfile.TemporaryDirectory() as temporary_folder:
            file_path = Path(temporary_folder) / "invoice_january.pdf"
            file_path.write_text("Fake invoice content", encoding="utf-8")

            file_item = FolderScanner().scan(temporary_folder)[0]

            category, confidence, reason = FileClassifier().classify(file_item)

            self.assertEqual(category, "invoices")
            self.assertEqual(confidence, "high")
            self.assertIn("invoice", reason.lower())

    def test_classifies_contract_by_name(self):
        with tempfile.TemporaryDirectory() as temporary_folder:
            file_path = Path(temporary_folder) / "contract_client_acme.docx"
            file_path.write_text("Fake contract content", encoding="utf-8")

            file_item = FolderScanner().scan(temporary_folder)[0]

            category, confidence, reason = FileClassifier().classify(file_item)

            self.assertEqual(category, "contracts")
            self.assertEqual(confidence, "high")
            self.assertIn("contract", reason.lower())

    def test_classifies_image_by_extension(self):
        with tempfile.TemporaryDirectory() as temporary_folder:
            file_path = Path(temporary_folder) / "unknown_image.png"
            file_path.write_text("", encoding="utf-8")

            file_item = FolderScanner().scan(temporary_folder)[0]

            category, confidence, reason = FileClassifier().classify(file_item)

            self.assertEqual(category, "images")
            self.assertEqual(confidence, "medium")
            self.assertIn("image", reason.lower())

    def test_classifies_video_by_extension(self):
        with tempfile.TemporaryDirectory() as temporary_folder:
            file_path = Path(temporary_folder) / "demo_video.mp4"
            file_path.write_text("", encoding="utf-8")

            file_item = FolderScanner().scan(temporary_folder)[0]

            category, confidence, reason = FileClassifier().classify(file_item)

            self.assertEqual(category, "videos")
            self.assertEqual(confidence, "medium")
            self.assertIn("video", reason.lower())

    def test_classifies_archive_by_extension(self):
        with tempfile.TemporaryDirectory() as temporary_folder:
            file_path = Path(temporary_folder) / "backup.zip"
            file_path.write_text("", encoding="utf-8")

            file_item = FolderScanner().scan(temporary_folder)[0]

            category, confidence, reason = FileClassifier().classify(file_item)

            self.assertEqual(category, "archives")
            self.assertEqual(confidence, "medium")
            self.assertIn("archive", reason.lower())

    def test_classifies_unknown_file_as_others(self):
        with tempfile.TemporaryDirectory() as temporary_folder:
            file_path = Path(temporary_folder) / "random_file.bin"
            file_path.write_text("", encoding="utf-8")

            file_item = FolderScanner().scan(temporary_folder)[0]

            category, confidence, reason = FileClassifier().classify(file_item)

            self.assertEqual(category, "others")
            self.assertEqual(confidence, "low")
            self.assertIn("no clear", reason.lower())


class TestMovePlanner(unittest.TestCase):
    def test_create_plan_returns_move_plans_without_moving_files(self):
        with tempfile.TemporaryDirectory() as temporary_folder:
            folder = Path(temporary_folder)

            invoice_file = folder / "invoice_january.pdf"
            invoice_file.write_text("Fake invoice content", encoding="utf-8")

            scanner = FolderScanner()
            files = scanner.scan(folder)

            planner = MovePlanner()
            plans = planner.create_plan(folder, files)

            self.assertEqual(len(plans), 1)

            plan = plans[0]

            self.assertEqual(plan.source_path, invoice_file)
            self.assertEqual(plan.target_path, folder / "invoices" / "invoice_january.pdf")
            self.assertEqual(plan.category, "invoices")
            self.assertEqual(plan.confidence, "high")
            self.assertTrue(plan.approved)

            self.assertTrue(invoice_file.exists())
            self.assertFalse((folder / "invoices" / "invoice_january.pdf").exists())


if __name__ == "__main__":
    unittest.main()