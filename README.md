# MOAZ Folder Management

## Overview

`MOAZ Folder Management` is a Python script designed to simplify folder management tasks. The script provides a graphical user interface (GUI) built with the wxPython library, allowing users to copy folders and files with various configuration options.

## Features

### 1. Copy Folders

- **Description:**
  - Copy selected folders and files to a specified destination.
  
- **Options:**
  - **Override:**
    - Enable this option to override existing files.
  - **Delete Source:**
    - If enabled, the source folder will be deleted after a successful copy.
  - **Skipping Existing Files:**
    - Skip copying files that already exist in the destination.
  - **Error Handling:**
    - Choose to skip errors during the copy process.

### 2. User-Friendly Interface

- **Graphical Interface:**
  - Provides an intuitive GUI for ease of interaction.
  - Log area displays progress and log messages.

### 3. Folder and File Selection

- **Browse and Select:**
  - Interactive folder and file selection.
  - Import folder and file paths from a text file.

## Prerequisites

Ensure you have the following prerequisites installed:

- Python 3
- wxPython (`pip install wxPython`)
- Pillow (`pip install Pillow`)

## Usage

1. **Run the Script:**
   ```bash
   python moaz_folder_management.py


--------------------------------------------------------------
GUI Usage:
Specify the destination path.
Select folders and files for copying.
Configure options like skipping existing files, handling errors, etc.
Click the "Copy Folders" button to initiate the copy process.
GUI Description
New Path:

Specify the destination path where folders will be copied.
Copy Folders:

Button to initiate the folder copy process.
Override:

Checkbox to enable overriding existing files.
Selected Folders:

Text area to display and select folders for copying.
Browse:

Button to browse and select folders interactively.
Selected Files:

Text area to display and select files for copying.
Import from File:

Button to import folder and file paths from a text file.
Progress Bar:

Indicates the progress of the copy operation.
Options:

Checkboxes for additional copy options like deleting the source after copying, skipping existing files, handling errors, and forcing the copy.
Clear:

Button to clear all input fields.
Log Area:

Displays progress updates and log messages.
Notes
The script uses the wxPython library for the graphical user interface.
Logging information is displayed in the log area.
Contributing
Contributions are welcome! If you find a bug or have suggestions, please create an issue or a pull request.


