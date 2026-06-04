import tkinter as tk
from pathlib import Path
from tkinter import filedialog, messagebox, ttk

from app.core.planner import MovePlanner
from app.core.scanner import FolderScanner
from app.models.move_plan import MovePlan

from app.core.organizer import FolderOrganizer

from app.core.rollback import RollbackManager

from app.core.summary import SummaryService

class FolderOrganizerApp:
    def __init__(self, root: tk.Tk) -> None:
        self.root = root
        self.root.title("Folder Organizer")
        self.root.geometry("1150x650")
        self.root.minsize(950, 520)

        self.selected_folder: Path | None = None
        self.current_plans: list[MovePlan] = []

        self.scanner = FolderScanner()
        self.planner = MovePlanner()
        self.organizer = FolderOrganizer()
        self.rollback_manager = RollbackManager()
        self.summary_service = SummaryService()

        self._configure_styles()
        self._build_layout()

    def _configure_styles(self) -> None:
        style = ttk.Style()

        try:
            style.theme_use("clam")
        except tk.TclError:
            pass

        style.configure(
            "Treeview",
            rowheight=28,
            font=("Segoe UI", 10),
        )

        style.configure(
            "Treeview.Heading",
            font=("Segoe UI", 10, "bold"),
        )

        style.configure(
            "Title.TLabel",
            font=("Segoe UI", 18, "bold"),
        )

        style.configure(
            "Subtitle.TLabel",
            font=("Segoe UI", 10),
        )

        style.configure(
            "Status.TLabel",
            font=("Segoe UI", 10),
        )

        style.configure(
            "Primary.TButton",
            font=("Segoe UI", 10, "bold"),
            padding=(14, 8),
            background="#2563EB",
            foreground="white",
        )

        style.map(
            "Primary.TButton",
            background=[
                ("active", "#1D4ED8"),
                ("pressed", "#1E40AF"),
                ("disabled", "#CBD5E1"),
            ],
            foreground=[
                ("disabled", "#64748B"),
            ],
        )

        style.configure(
            "Secondary.TButton",
            font=("Segoe UI", 10),
            padding=(12, 8),
        )

    def _build_layout(self) -> None:
        header_frame = ttk.Frame(self.root, padding=(16, 14, 16, 8))
        header_frame.pack(fill="x")

        title_label = ttk.Label(
            header_frame,
            text="Folder Organizer",
            style="Title.TLabel",
        )
        title_label.pack(anchor="w")

        description_label = ttk.Label(
            header_frame,
            text="Select a folder, review the proposed organization, and approve changes before moving anything.",
            style="Subtitle.TLabel",
        )
        description_label.pack(anchor="w", pady=(4, 0))

        controls_frame = ttk.Frame(self.root, padding=(16, 8, 16, 8))
        controls_frame.pack(fill="x")

        self.folder_label_var = tk.StringVar(value="No folder selected")

        folder_label = ttk.Label(
            controls_frame,
            textvariable=self.folder_label_var,
        )
        folder_label.pack(side="left", fill="x", expand=True)

        buttons_frame = ttk.Frame(controls_frame)
        buttons_frame.pack(side="right", padx=(16, 0))

        select_button = ttk.Button(
            buttons_frame,
            text="📁 Select folder",
            command=self.select_folder,
            style="Secondary.TButton",
        )
        select_button.pack(side="left")

        self.scan_button = ttk.Button(
        buttons_frame,
        text="🔍 Scan folder",
        command=self.scan_folder,
        style="Primary.TButton",
        state="disabled",
        )
        self.scan_button.pack(side="left", padx=(18, 0))

        helper_frame = ttk.Frame(self.root, padding=(16, 0, 16, 4))
        helper_frame.pack(fill="x")

        helper_label = ttk.Label(
            helper_frame,
            text="Preview only: no files will be moved until you explicitly apply approved movements.",
        )
        helper_label.pack(anchor="w")

        table_frame = ttk.Frame(self.root, padding=(16, 8, 16, 8))
        table_frame.pack(fill="both", expand=True)

        columns = (
            "approved",
            "file_name",
            "category",
            "confidence",
            "destination",
            "reason",
        )

        self.preview_table = ttk.Treeview(
            table_frame,
            columns=columns,
            show="headings",
            height=18,
        )

        self.preview_table.heading("approved", text="Action")
        self.preview_table.heading("file_name", text="File name")
        self.preview_table.heading("category", text="Category")
        self.preview_table.heading("confidence", text="Confidence")
        self.preview_table.heading("destination", text="Destination")
        self.preview_table.heading("reason", text="Reason")

        self.preview_table.column("approved", width=100, anchor="center", stretch=False)
        self.preview_table.column("file_name", width=230, anchor="w")
        self.preview_table.column("category", width=130, anchor="center", stretch=False)
        self.preview_table.column("confidence", width=110, anchor="center", stretch=False)
        self.preview_table.column("destination", width=260, anchor="w")
        self.preview_table.column("reason", width=330, anchor="w")

        self.preview_table.bind("<Double-1>", self.toggle_selected_plan_approval)

        self.preview_table.tag_configure("high", background="#EAF7EA")
        self.preview_table.tag_configure("medium", background="#FFF7E6")
        self.preview_table.tag_configure("low", background="#FDECEC")
        self.preview_table.tag_configure("not_approved", background="#F1F5F9")
        self.preview_table.tag_configure("not_approved", background="#F1F5F9")

        vertical_scrollbar = ttk.Scrollbar(
            table_frame,
            orient="vertical",
            command=self.preview_table.yview,
        )

        horizontal_scrollbar = ttk.Scrollbar(
            table_frame,
            orient="horizontal",
            command=self.preview_table.xview,
        )

        self.preview_table.configure(
            yscrollcommand=vertical_scrollbar.set,
            xscrollcommand=horizontal_scrollbar.set,
        )

        self.preview_table.grid(row=0, column=0, sticky="nsew")
        vertical_scrollbar.grid(row=0, column=1, sticky="ns")
        horizontal_scrollbar.grid(row=1, column=0, sticky="ew")

        table_frame.rowconfigure(0, weight=1)
        table_frame.columnconfigure(0, weight=1)

        footer_frame = ttk.Frame(self.root, padding=(16, 8, 16, 14))
        footer_frame.pack(fill="x")

        self.status_var = tk.StringVar(value="Ready")

        status_label = ttk.Label(
            footer_frame,
            textvariable=self.status_var,
            style="Status.TLabel",
        )
        status_label.pack(side="left")

        self.apply_button = ttk.Button(
            footer_frame,
            text="Apply approved movements",
            command=self.apply_approved_movements,
            state="disabled",
        )
        self.apply_button.pack(side="right")

        self.undo_button = ttk.Button(
            footer_frame,
            text="Undo last operation",
            command=self.undo_last_operation,
            state="normal",
        )
        self.undo_button.pack(side="right", padx=(0, 8))

        self.toggle_approval_button = ttk.Button(
            footer_frame,
            text="☑/☐ Change selected",
            command=self.toggle_selected_plan_approval,
            state="disabled",
        )
        self.toggle_approval_button.pack(side="right", padx=(0, 8))

    def select_folder(self) -> None:
        folder = filedialog.askdirectory(title="Select a folder to organize")

        if not folder:
            return

        self.selected_folder = Path(folder)
        self.folder_label_var.set(f"Selected folder: {self.selected_folder}")
        self.status_var.set("Folder selected. Ready to scan.")
        self.scan_button.configure(state="normal")

    def scan_folder(self) -> None:
        if self.selected_folder is None:
            messagebox.showwarning(
                "No folder selected",
                "Please select a folder before scanning.",
            )
            return

        try:
            files = self.scanner.scan(self.selected_folder)
            self.current_plans = self.planner.create_plan(
                self.selected_folder,
                files,
            )
        except Exception as error:
            messagebox.showerror("Scan error", str(error))
            return

        self._populate_preview_table()
        self.status_var.set(f"Scan complete. {len(self.current_plans)} files found.")

        if self.current_plans:
            self.toggle_approval_button.configure(state="normal")
            self.apply_button.configure(state="normal")

    def _populate_preview_table(self) -> None:
        for item in self.preview_table.get_children():
            self.preview_table.delete(item)

        for index, plan in enumerate(self.current_plans):
            relative_destination = self._get_relative_destination(plan.target_path)

            self.preview_table.insert(
                "",
                "end",
                iid=str(index),
                values=(
                    "☑ Move" if plan.approved else "☐ Skip",
                    plan.file_item.name,
                    plan.category,
                    plan.confidence,
                    relative_destination,
                    plan.reason,
                ),
                tags=("not_approved",) if not plan.approved else (plan.confidence,),
            )

    def toggle_selected_plan_approval(self, event=None) -> None:
        selected_items = self.preview_table.selection()

        if not selected_items:
            messagebox.showinfo(
                "No file selected",
                "Please select a file from the preview table first.",
            )
            return

        selected_item = selected_items[0]
        plan_index = int(selected_item)

        plan = self.current_plans[plan_index]
        plan.approved = not plan.approved

        self._populate_preview_table()

        status = "approved" if plan.approved else "not approved"
        self.status_var.set(f"{plan.file_item.name} marked as {status}.")

    def _get_relative_destination(self, target_path: Path) -> str:
        if self.selected_folder is None:
            return str(target_path)

        try:
            return str(target_path.relative_to(self.selected_folder))
        except ValueError:
            return str(target_path)
    def apply_approved_movements(self) -> None:
        if self.selected_folder is None:
            messagebox.showwarning(
                "No folder selected",
                "Please select a folder first.",
            )
            return

        approved_count = sum(1 for plan in self.current_plans if plan.approved)

        if approved_count == 0:
            messagebox.showinfo(
                "No files approved",
                "There are no files marked as ☑ Move.",
            )
            return

        confirmed = messagebox.askyesno(
            "Confirm organization",
            f"{approved_count} files will be moved. Do you want to continue?",
        )

        if not confirmed:
            return

        try:
            operation_log = self.organizer.apply(
                self.selected_folder,
                self.current_plans,
            )
        except Exception as error:
            messagebox.showerror("Organization error", str(error))
            return

        moved_count = len(operation_log.movements)
        summary_path = self.summary_service.export_operation_summary(operation_log)

        messagebox.showinfo(
            "Organization complete",
            (
                f"{moved_count} files were moved successfully.\n\n"
                f"Summary exported to:\n{summary_path}"
            ),
        )

        self.status_var.set(
            f"Organization complete. {moved_count} files moved. Summary exported."
        )
        self.apply_button.configure(state="disabled")
        self.toggle_approval_button.configure(state="disabled")

        files = self.scanner.scan(self.selected_folder)
        self.current_plans = self.planner.create_plan(self.selected_folder, files)
        self._populate_preview_table()

    def undo_last_operation(self) -> None:
        confirmed = messagebox.askyesno(
            "Undo last operation",
            "This will try to move files from the latest organization back to their original locations. Do you want to continue?",
        )

        if not confirmed:
            return

        try:
            restored_count = self.rollback_manager.undo_last_operation()
        except Exception as error:
            messagebox.showerror("Undo error", str(error))
            return

        if restored_count == 0:
            messagebox.showinfo(
                "Nothing to undo",
                "No files were restored. There may be no previous operation log, or the files may have already been moved.",
            )
            self.status_var.set("Nothing to undo.")
            return

        messagebox.showinfo(
            "Undo complete",
            f"{restored_count} files were restored successfully.",
        )

        self.status_var.set(f"Undo complete. {restored_count} files restored.")

        if self.selected_folder is not None:
            files = self.scanner.scan(self.selected_folder)
            self.current_plans = self.planner.create_plan(self.selected_folder, files)
            self._populate_preview_table()

def run_app() -> None:
    root = tk.Tk()
    FolderOrganizerApp(root)
    root.mainloop()