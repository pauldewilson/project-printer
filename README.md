# Project Printer

![Python Version](https://img.shields.io/badge/python-3.12-blue)
![Project Version](https://img.shields.io/badge/version-0.2-orange)
![License](https://img.shields.io/badge/license-MIT-brightgreen)
![Build Status](https://img.shields.io/badge/build-passing-brightgreen)
![Contributions Welcome](https://img.shields.io/badge/contributions-welcome-brightgreen)

This project provides a Python-based tool designed to display a directory tree and optionally print the contents of specific files. It supports excluding files and directories based on patterns specified in a `.gitignore` file, making it ideal for developers who need to share project structures and contents in a reproducible way, such as in code reviews or with ChatGPT.

## Table of Contents

- [Features](#features)
- [Requirements](#requirements)
- [Installation](#installation)
- [Usage](#usage)
- [Example Configuration (`template.yml`)](#example-configuration-projyml)
- [Example Output (per Example Configuration)](#example-output-per-example-configuration)
- [Change Log](#change-log)

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
    git clone https://github.com/pauldewilson/project-printer
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
1. Configure the directories and files to be processed by modifying the `template.yml` file.
2. Run the script:
    ```sh
    python printer.py --config template.yml [--clipboard] [--dironly]
    ```
    - `--clipboard`: Copy the output to the clipboard.
    - `--dironly`: Print only the directory structure, without file contents.

## Example Configuration (`template.yml`)
```yaml
dirs:
  - C:\Dev\project-printer
files:
  - C:\Dev\project-printer\printer.py
regexfiles:
  - dir: C:\Dev\project-printer\tests\
    pattern: '^(?!__init__\.py$).*\.py$'
    subdirs: true
gitignore: C:\Dev\project-printer\.gitignore
```

## Example output (per Example Configuration)
**Note: The entirity of the visible contents below the horizontal line is what would be output to the terminal and optionally added to clipboard**
<hr>

Directory: C:\Dev\project-printer

+---project-printer
    +---.gitignore<br>
    +---.pylintrc<br>
    +---LICENSE<br>
    +---printer.py<br>
    +---README.md<br>
    +---requirements.txt<br>
    +---template.yml<br>
    +---__init__.py<br>
    +---tests<br>
        +---test_printer.py<br>
        +---test_regexfile.py<br>
        +---__init__.py<br>
venv

File: C:\Dev\project-printer\printer.py

\`\`\`<br>
import os
*...rest of printer py file*

\`\`\`

File: C:\Dev\project-printer\tests\test_printer.py

\`\`\`<br>
import os
*...rest of test_printer py file*

\`\`\`

File: C:\Dev\project-printer\tests\test_regexfile.py

\`\`\`<br>
import os
*...rest of printer py file*

\`\`\`

Output has been copied to the clipboard.

## Change Log

All notable changes to this project will be documented in this section.

### [0.2] - 2024-10-04

#### Added
- Introduced the ability to search directories using regex with the `regexfiles` YAML key.
- Created tests to validate `regexfiles` functionality.

#### Changed
- Moved tests to the `./tests/` directory.

### [0.1] - 2024-08-26

#### Added
- Initial project creation.
