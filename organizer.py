from __future__ import annotations

import hashlib
import shutil
from collections import defaultdict
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path


FILE_TYPES = {
    "Images": {".jpg", ".jpeg", ".png", ".gif", ".bmp", ".webp", ".tiff", ".svg"},
    "Audio": {".mp3", ".wav", ".flac", ".aac", ".ogg", ".m4a", ".wma"},
    "Documents": {
        ".pdf", ".doc", ".docx", ".txt", ".rtf", ".odt", ".xls",
        ".xlsx", ".csv", ".ppt", ".pptx",
    },
    "Videos": {".mp4", ".mkv", ".avi", ".mov", ".wmv", ".flv", ".webm"},
    "Archives": {".zip", ".rar", ".7z", ".tar", ".gz"},
    "Programs": {".exe", ".msi", ".apk", ".bat", ".cmd"},
}


@dataclass
class DuplicateGroup:
    hash_value: str
    files: list[Path]


@dataclass
class OrganizationReport:
    scanned: int = 0
    organized: int = 0
    duplicates: int = 0
    errors: int = 0
    duplicate_groups: list[DuplicateGroup] | None = None

    def __post_init__(self) -> None:
        if self.duplicate_groups is None:
            self.duplicate_groups = []


def category_for(path: Path) -> str:
    suffix = path.suffix.lower()
    for category, extensions in FILE_TYPES.items():
        if suffix in extensions:
            return category
    return "Others"


def file_hash(path: Path, chunk_size: int = 1024 * 1024) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as source:
        for chunk in iter(lambda: source.read(chunk_size), b""):
            digest.update(chunk)
    return digest.hexdigest()


def unique_destination(destination: Path) -> Path:
    if not destination.exists():
        return destination

    stem = destination.stem
    suffix = destination.suffix
    counter = 1
    while True:
        candidate = destination.with_name(f"{stem} ({counter}){suffix}")
        if not candidate.exists():
            return candidate
        counter += 1


def find_duplicates(paths: list[Path]) -> list[DuplicateGroup]:
    by_hash: dict[str, list[Path]] = defaultdict(list)
    for path in paths:
        if path.is_file():
            try:
                by_hash[file_hash(path)].append(path)
            except OSError:
                continue

    return [
        DuplicateGroup(hash_value=digest, files=files)
        for digest, files in by_hash.items()
        if len(files) > 1
    ]


def organize_folder(source_folder: str | Path, mode: str = "type") -> OrganizationReport:
    source = Path(source_folder).expanduser()
    if not source.exists():
        raise FileNotFoundError(f"Folder does not exist: {source}")
    if not source.is_dir():
        raise NotADirectoryError(f"Path is not a folder: {source}")
    if mode not in {"type", "date"}:
        raise ValueError("Mode must be either 'type' or 'date'")

    report = OrganizationReport()
    files = [entry for entry in source.iterdir() if entry.is_file()]
    report.scanned = len(files)

    duplicate_groups = find_duplicates(files)
    report.duplicate_groups = duplicate_groups
    report.duplicates = sum(len(group.files) - 1 for group in duplicate_groups)

    for file_path in files:
        try:
            if mode == "type":
                destination_folder = source / category_for(file_path)
            else:
                modified = datetime.fromtimestamp(file_path.stat().st_mtime)
                destination_folder = source / modified.strftime("%Y-%m")

            destination_folder.mkdir(parents=True, exist_ok=True)
            destination = unique_destination(destination_folder / file_path.name)
            if destination == file_path:
                continue
            shutil.move(str(file_path), str(destination))
            report.organized += 1
        except OSError:
            report.errors += 1

    return report
