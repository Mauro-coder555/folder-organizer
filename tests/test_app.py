import tempfile
import unittest
from pathlib import Path

from app.core.classifier import FileClassifier
from app.core.planner import MovePlanner
from app.core.scanner import FolderScanner

from app.core.organizer import FolderOrganizer
from app.storage.log_repository import LogRepository

from app.core.rollback import RollbackManager

from app.core.summary import SummaryService
from app.storage.markdown_exporter import MarkdownExporter


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

class TestFolderOrganizer(unittest.TestCase):
    def test_apply_moves_only_approved_files_and_saves_log(self):
        with tempfile.TemporaryDirectory() as temporary_folder:
            folder = Path(temporary_folder)
            logs_folder = folder / "logs"

            invoice_file = folder / "invoice_january.pdf"
            notes_file = folder / "notes.txt"

            invoice_file.write_text("Fake invoice content", encoding="utf-8")
            notes_file.write_text("Some notes", encoding="utf-8")

            files = FolderScanner().scan(folder)
            plans = MovePlanner().create_plan(folder, files)

            for plan in plans:
                if plan.file_item.name == "notes.txt":
                    plan.approved = False

            log_repository = LogRepository(logs_folder=logs_folder)
            organizer = FolderOrganizer(log_repository=log_repository)

            operation_log = organizer.apply(folder, plans)

            moved_invoice = folder / "invoices" / "invoice_january.pdf"
            skipped_notes = folder / "notes.txt"

            self.assertTrue(moved_invoice.exists())
            self.assertFalse(invoice_file.exists())
            self.assertTrue(skipped_notes.exists())

            self.assertEqual(len(operation_log.movements), 1)
            self.assertEqual(operation_log.movements[0].file_name, "invoice_january.pdf")

            saved_logs = list(logs_folder.glob("*.json"))
            self.assertEqual(len(saved_logs), 1)

    def test_apply_does_not_overwrite_existing_files(self):
        with tempfile.TemporaryDirectory() as temporary_folder:
            folder = Path(temporary_folder)
            logs_folder = folder / "logs"

            source_invoice = folder / "invoice_january.pdf"
            target_folder = folder / "invoices"
            existing_invoice = target_folder / "invoice_january.pdf"

            source_invoice.write_text("New invoice", encoding="utf-8")
            target_folder.mkdir()
            existing_invoice.write_text("Existing invoice", encoding="utf-8")

            files = FolderScanner().scan(folder)
            plans = MovePlanner().create_plan(folder, files)

            log_repository = LogRepository(logs_folder=logs_folder)
            organizer = FolderOrganizer(log_repository=log_repository)

            operation_log = organizer.apply(folder, plans)

            safe_target = folder / "invoices" / "invoice_january_1.pdf"

            self.assertTrue(existing_invoice.exists())
            self.assertTrue(safe_target.exists())
            self.assertEqual(existing_invoice.read_text(encoding="utf-8"), "Existing invoice")
            self.assertEqual(safe_target.read_text(encoding="utf-8"), "New invoice")

            self.assertEqual(len(operation_log.movements), 1)
            self.assertEqual(operation_log.movements[0].target_path, safe_target)


class TestRollbackManager(unittest.TestCase):
    def test_undo_last_operation_restores_moved_files(self):
        with tempfile.TemporaryDirectory() as temporary_folder:
            folder = Path(temporary_folder)
            logs_folder = folder / "logs"

            invoice_file = folder / "invoice_january.pdf"
            invoice_file.write_text("Fake invoice content", encoding="utf-8")

            files = FolderScanner().scan(folder)
            plans = MovePlanner().create_plan(folder, files)

            log_repository = LogRepository(logs_folder=logs_folder)
            organizer = FolderOrganizer(log_repository=log_repository)
            organizer.apply(folder, plans)

            moved_invoice = folder / "invoices" / "invoice_january.pdf"

            self.assertFalse(invoice_file.exists())
            self.assertTrue(moved_invoice.exists())

            rollback_manager = RollbackManager(log_repository=log_repository)
            restored_count = rollback_manager.undo_last_operation()

            self.assertEqual(restored_count, 1)
            self.assertTrue(invoice_file.exists())
            self.assertFalse(moved_invoice.exists())

    def test_undo_last_operation_returns_zero_when_no_log_exists(self):
        with tempfile.TemporaryDirectory() as temporary_folder:
            logs_folder = Path(temporary_folder) / "logs"

            log_repository = LogRepository(logs_folder=logs_folder)
            rollback_manager = RollbackManager(log_repository=log_repository)

            restored_count = rollback_manager.undo_last_operation()

            self.assertEqual(restored_count, 0)

    class TestSummaryService(unittest.TestCase):
        def test_export_operation_summary_creates_markdown_file(self):
            with tempfile.TemporaryDirectory() as temporary_folder:
                folder = Path(temporary_folder)
                logs_folder = folder / "logs"
                summaries_folder = folder / "summaries"

                invoice_file = folder / "invoice_january.pdf"
                invoice_file.write_text("Fake invoice content", encoding="utf-8")

                files = FolderScanner().scan(folder)
                plans = MovePlanner().create_plan(folder, files)

                log_repository = LogRepository(logs_folder=logs_folder)
                organizer = FolderOrganizer(log_repository=log_repository)
                operation_log = organizer.apply(folder, plans)

                markdown_exporter = MarkdownExporter(summaries_folder=summaries_folder)
                summary_service = SummaryService(markdown_exporter=markdown_exporter)

                summary_path = summary_service.export_operation_summary(operation_log)

                self.assertTrue(summary_path.exists())
                self.assertEqual(summary_path.suffix, ".md")

                content = summary_path.read_text(encoding="utf-8")

                self.assertIn("# Folder Organization Summary", content)
                self.assertIn("invoice_january.pdf", content)
                self.assertIn("invoices", content)
                self.assertIn("Files moved", content)

if __name__ == "__main__":
    unittest.main()