# Project Printer

![Python Version](https://img.shields.io/badge/python-3.12-blue)
![Project Version](https://img.shields.io/badge/version-0.2.3-orange)
![License](https://img.shields.io/badge/license-MIT-brightgreen)
![Build Status](https://img.shields.io/badge/build-passing-brightgreen)
![Contributions Welcome](https://img.shields.io/badge/contributions-welcome-brightgreen)

This project provides a Python-based tool designed to display a directory tree and optionally print the contents of specific files. It supports excluding files and directories based on patterns specified in a `.gitignore` file, making it ideal for developers who need to share project structures and contents in a reproducible way, such as in code reviews or with AI assistants like ChatGPT and Claude.

## Table of Contents

- [Features](#features)
- [Requirements](#requirements)
- [Installation](#installation)
- [Usage](#usage)
- [Example Configuration (`template.yml`)](#example-configuration-templateyml)
- [Example Output (per Example Configuration)](#example-output-per-example-configuration)
- [Using with AI Assistants](#using-with-ai-assistants)
- [Change Log](#change-log)

## Features
- **Directory Tree Display:** Displays the directory structure of specified paths.
- **File Content Display:** Optionally prints the contents of specified files.
- **Jupyter Notebook Support:** Automatically converts `.ipynb` files to Python code for cleaner output.
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
python printer.py --config template.yml [--clipboard] [--dironly] [--nodirtree]
```

- `--clipboard`: Copy the output to the clipboard.
- `--dironly`: Print only the directory structure, without file contents.
- `--nodirtree`: Do not print directory structure.

## Example Configuration (`template.yml`)
```yaml
dirs:
  - C:\Dev\project-printer
files:
  - C:\Dev\project-printer\printer.py
  - C:\Dev\project-printer\data\analysis.ipynb
regexfiles:
  - dir: C:\Dev\project-printer\tests\
    pattern: '^(?!__init__\.py$).*\.py$'
    subdirs: true
  - dir: C:\Dev\project-printer\notebooks\
    pattern: '.*\.ipynb$'
    subdirs: true
gitignore: C:\Dev\project-printer\.gitignore
```

## Example Output (per Example Configuration)
**Note: The entirety of the visible contents below the horizontal line is what would be output to the terminal and optionally added to clipboard**

---

```
Directory: C:\Dev\project-printer

+---project-printer
    +---.gitignore
    +---.pylintrc
    +---LICENSE
    +---printer.py
    +---README.md
    +---requirements.txt
    +---template.yml
    +---__init__.py
    +---tests
        +---test_printer.py
        +---test_regexfile.py
        +---__init__.py
    +---data
        +---analysis.ipynb
    +---notebooks
        +---example.ipynb
venv

File: C:\Dev\project-printer\printer.py

```
import os
*...rest of printer py file*
```

File: C:\Dev\project-printer\data\analysis.ipynb

```
# Generated from C:\Dev\project-printer\data\analysis.ipynb

# Code cell 1
import pandas as pd
import numpy as np

data = pd.read_csv('data.csv')
print(data.head())

# Code cell 2
data.describe()
```

File: C:\Dev\project-printer\tests\test_printer.py

```
import os
*...rest of test_printer py file*
```

File: C:\Dev\project-printer\tests\test_regexfile.py

```
import os
*...rest of printer py file*
```

File: C:\Dev\project-printer\notebooks\example.ipynb

```
# Generated from C:\Dev\project-printer\notebooks\example.ipynb

# Example notebook
import matplotlib.pyplot as plt

x = np.linspace(0, 10, 100)
y = np.sin(x)

plt.plot(x, y)
plt.show()
```

Output has been copied to the clipboard.
```

## Using with AI Assistants

Project Printer is particularly useful for sharing code with AI assistants like ChatGPT and Claude. Here's how to use it effectively:

### Suggested Workflow

1. Create a template file for your project:
```yaml
# my-project.yml
dirs:
  - C:\path\to\your\project
files:
  - C:\path\to\your\project\important_file.py
regexfiles:
  - dir: C:\path\to\your\project\src
    pattern: '.*\.py$'
    subdirs: true
gitignore: C:\path\to\your\project\.gitignore
```

2. Run Project Printer with the clipboard option:
```sh
python printer.py --config my-project.yml --clipboard
```

3. Paste the output directly into your conversation with an AI assistant.

### Prompt Templates for AI Assistants

When sharing code with AI assistants, try these prompt templates:

#### General Code Review
```
I'm sharing my project structure and code with you. Please review it and suggest improvements for readability, performance, and best practices:

[PASTE PROJECT PRINTER OUTPUT HERE]
```

#### Specific Code Questions
```
Here's my project structure and relevant files. I'm having trouble with [SPECIFIC ISSUE]. Can you help me understand what's going wrong and how to fix it?

[PASTE PROJECT PRINTER OUTPUT HERE]
```

#### Learning and Explanation
```
I'm learning [LANGUAGE/FRAMEWORK]. Here's a project I'm working through. Could you explain how the different parts connect and what each file is doing?

[PASTE PROJECT PRINTER OUTPUT HERE]
```

#### Project Extension
```
Here's my current project. I want to add [NEW FEATURE]. How would you recommend implementing this given my current codebase?

[PASTE PROJECT PRINTER OUTPUT HERE]
```

## Change Log

All notable changes to this project will be documented in this section.

### [0.2.3] - 2025-04-03

#### Added
- Jupyter Notebook (`.ipynb`) support: automatically converts notebook files to Python code for cleaner output
- Test suite for Jupyter Notebook conversion functionality

### [0.2.2] - 2024-11-28

#### Added
- `--nodirtree` argument added which, when provided, will not print or copy the blue directory tree structure

### [0.2.1] - 2024-10-04

#### Changed
- Files and directories that are not found are always printed last, in red

### [0.2] - 2024-10-04

#### Added
- Introduced the ability to search directories using regex with the `regexfiles` YAML key.
- Created tests to validate `regexfiles` functionality.

#### Changed
- Moved tests to the `./tests/` directory.

### [0.1] - 2024-08-26

#### Added
- Initial project creation.
