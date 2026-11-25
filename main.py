import tkinter as tk
from tkinter import filedialog, messagebox, ttk
from pathlib import Path

from organizer import OrganizationReport, organize_folder


class SmartFileOrganizerApp:
    def __init__(self, root: tk.Tk) -> None:
        self.root = root
        self.root.title("Smart File Organizer")
        self.root.geometry("760x560")
        self.root.minsize(680, 520)
        self.folder = tk.StringVar()
        self.mode = tk.StringVar(value="type")

        self._build_ui()

    def _build_ui(self) -> None:
        main = ttk.Frame(self.root, padding=20)
        main.pack(fill="both", expand=True)

        title = ttk.Label(main, text="Smart File Organizer", font=("Segoe UI", 22, "bold"))
        title.pack(anchor="w")
        ttk.Label(
            main,
            text="Arrange files automatically and find duplicates in a selected folder.",
            foreground="#555555",
        ).pack(anchor="w", pady=(0, 18))

        folder_frame = ttk.LabelFrame(main, text="Folder to organize", padding=12)
        folder_frame.pack(fill="x")
        path_row = ttk.Frame(folder_frame)
        path_row.pack(fill="x")
        self.folder_entry = ttk.Entry(path_row, textvariable=self.folder)
        self.folder_entry.pack(side="left", fill="x", expand=True, padx=(0, 10))
        ttk.Button(path_row, text="Browse...", command=self.choose_folder).pack(side="right")

        options = ttk.LabelFrame(main, text="Organization method", padding=12)
        options.pack(fill="x", pady=12)
        ttk.Radiobutton(
            options, text="By file type", variable=self.mode, value="type"
        ).pack(side="left", padx=(0, 25))
        ttk.Radiobutton(
            options, text="By modification date", variable=self.mode, value="date"
        ).pack(side="left")

        button_row = ttk.Frame(main)
        button_row.pack(fill="x", pady=(0, 12))
        self.organize_button = ttk.Button(
            button_row, text="Organize files", command=self.organize_files
        )
        self.organize_button.pack(side="left")
        ttk.Button(button_row, text="Clear report", command=self.clear_report).pack(
            side="left", padx=8
        )

        report_frame = ttk.LabelFrame(main, text="Report and duplicate alerts", padding=12)
        report_frame.pack(fill="both", expand=True)
        self.report = tk.Text(
            report_frame,
            height=14,
            wrap="word",
            font=("Consolas", 10),
            state="disabled",
        )
        scrollbar = ttk.Scrollbar(report_frame, orient="vertical", command=self.report.yview)
        self.report.configure(yscrollcommand=scrollbar.set)
        self.report.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        self.write_report("Choose a folder, select an organization method, and start.")

    def choose_folder(self) -> None:
        selected = filedialog.askdirectory(title="Select the folder to organize")
        if selected:
            self.folder.set(selected)

    def clear_report(self) -> None:
        self.write_report("Report cleared. Choose a folder to begin.")

    def write_report(self, text: str) -> None:
        self.report.configure(state="normal")
        self.report.delete("1.0", "end")
        self.report.insert("1.0", text)
        self.report.configure(state="disabled")

    def organize_files(self) -> None:
        folder = self.folder.get().strip()
        if not folder:
            messagebox.showwarning("Folder required", "Please select a folder first.")
            return
        if not Path(folder).is_dir():
            messagebox.showerror("Invalid folder", "The selected folder does not exist.")
            return

        self.organize_button.configure(state="disabled")
        self.root.update_idletasks()
        try:
            result: OrganizationReport = organize_folder(folder, self.mode.get())
            self.show_result(result, folder)
        except (OSError, ValueError) as error:
            messagebox.showerror("Organization failed", str(error))
        finally:
            self.organize_button.configure(state="normal")

    def show_result(self, result: OrganizationReport, folder: str) -> None:
        lines = [
            "ORGANIZATION REPORT",
            "=" * 45,
            f"Folder: {folder}",
            f"Files scanned: {result.scanned}",
            f"Files organized: {result.organized}",
            f"Duplicate files detected: {result.duplicates}",
            f"Files skipped because of errors: {result.errors}",
            "",
        ]

        groups = result.duplicate_groups or []
        if groups:
            lines.append("DUPLICATE GROUPS")
            lines.append("-" * 45)
            for index, group in enumerate(groups, start=1):
                lines.append(f"{index}. {len(group.files)} copies")
                for duplicate in group.files:
                    lines.append(f"   - {duplicate.name}")
            lines.append("")

        self.write_report("\n".join(lines))
        if result.duplicates:
            messagebox.showwarning(
                "Duplicate files found",
                f"{result.duplicates} duplicate file(s) were found. "
                "They were not deleted; review the report before removing them.",
            )
        else:
            messagebox.showinfo(
                "Organization complete",
                f"Successfully organized {result.organized} file(s).",
            )


def main() -> None:
    root = tk.Tk()
    SmartFileOrganizerApp(root)
    root.mainloop()


if __name__ == "__main__":
    main()
