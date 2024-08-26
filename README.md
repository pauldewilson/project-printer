# Project Printer

This project provides a Python-based tool designed to display a directory tree and optionally print the contents of specific files. It supports excluding files and directories based on patterns specified in a `.gitignore` file, making it ideal for developers who need to share project structures and contents in a reproducible way, such as in code reviews or with ChatGPT.

## Features
- **Directory Tree Display:** Displays the directory structure of specified paths.
- **File Content Display:** Optionally prints the contents of specified files.
- **Gitignore Support:** Excludes files and directories based on patterns defined in a `.gitignore` file.
- **Clipboard Support:** Option to copy the generated output directly to the clipboard for easy pasting.

## Requirements
- Only tested on `Python 3.12`
- Required Python packages can be installed via `requirements.txt`.

## Installation
1. Clone the repository:
    ```sh
    git clone https://github.com/yourusername/project-printer.git
    ```
2. Navigate to the project directory:
    ```sh
    cd project-printer
    ```
3. (Optional) Set up a virtual environment:
    ```sh
    python -m venv venv
    source venv/bin/activate  # On Windows: venv\Scripts\activate
    ```
4. Install the required packages:
    ```sh
    pip install -r requirements.txt
    ```

## Usage
1. Configure the directories and files to be processed by modifying the `proj.yml` file.
2. Run the script:
    ```sh
    python printer.py --config proj.yml [--clipboard] [--dironly]
    ```
    - `--clipboard`: Copy the output to the clipboard.
    - `--dironly`: Print only the directory structure, without file contents.

## Example Configuration (`proj.yml`)
```yaml
dirs:
  - C:/Dev/project-printer
files:
  - C:/Dev/project-printer/printer.py
gitignore: C:/Dev/project-printer/.gitignore
```

## Example output (per Example Configuration)
**Note: The entirity of the visible contents below the horizontal line is what would be output to the terminal and optionally added to clipboard**
<hr>

Directory: C:\Dev\project-printer

project-printer
    +---.gitignore
    +---printer.py
    +---README.md
    +---requirements.txt
    +---template.yml
venv

File: C:\Dev\project-printer\printer.py

\`\`\`
import os
*...rest of printer py file*

\`\`\`

Output has been copied to the clipboard.
