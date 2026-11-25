# Smart File Organizer

A real desktop application for organizing files in a selected Windows folder.

## Features

- Organizes files into category folders: Images, Audio, Documents, Videos, Archives, Programs, and Others.
- Organizes files by modification year and month.
- Uses SHA-256 hashes to detect duplicate files.
- Keeps duplicate files in place and reports every copy without deleting data.
- Displays a summary report with scanned, organized, duplicate, and error counts.
- Provides a simple Tkinter desktop interface.

## Run

Python 3.10 or newer is required.

```powershell
cd "C:\Users\User\OneDrive\Desktop\100 Project\11"
python main.py
```

Tkinter is included with the standard Windows Python installation. No third-party packages are needed.

## Tests

```powershell
python -m unittest discover -s tests -v
```
