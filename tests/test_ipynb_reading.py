import os
import json
import tempfile
import shutil
import pytest
import pyperclip
import yaml
from io import StringIO
from unittest.mock import patch
from printer import print_tree_and_file_contents, convert_ipynb_to_py_content


@pytest.fixture
def temp_notebook():
    # Create a temporary directory
    temp_dir = tempfile.mkdtemp()

    # Create a sample notebook structure
    notebook_content = {
        "cells": [
            {
                "cell_type": "markdown",
                "metadata": {},
                "source": ["# This is a markdown cell that should be ignored"]
            },
            {
                "cell_type": "code",
                "execution_count": 1,
                "metadata": {},
                "source": [
                    "# This is Python code in a code cell\n",
                    "def hello_world():\n",
                    "    print(\"Hello, world!\")\n",
                    "\n",
                    "hello_world()"
                ],
                "outputs": []
            },
            {
                "cell_type": "code",
                "execution_count": 2,
                "metadata": {},
                "source": [
                    "# Another code cell\n",
                    "import numpy as np\n",
                    "data = np.array([1, 2, 3])\n",
                    "print(data)"
                ],
                "outputs": []
            },
            {
                "cell_type": "code",
                "execution_count": 3,
                "metadata": {},
                "source": [],  # Empty cell should be skipped
                "outputs": []
            }
        ],
        "metadata": {
            "kernelspec": {
                "display_name": "Python 3",
                "language": "python",
                "name": "python3"
            }
        },
        "nbformat": 4,
        "nbformat_minor": 4
    }

    # Create the notebook file
    notebook_path = os.path.join(temp_dir, "test_notebook.ipynb")
    with open(notebook_path, "w") as f:
        json.dump(notebook_content, f)

    # Create a config file that includes the notebook
    config_path = os.path.join(temp_dir, "test_config.yml")
    config_content = {
        "dirs": [temp_dir],
        "files": [notebook_path],
        "regexfiles": []
    }

    with open(config_path, "w") as f:
        f.write(yaml.dump(config_content))

    yield temp_dir, notebook_path, config_path

    # Clean up the temporary directory
    shutil.rmtree(temp_dir)


def test_convert_ipynb_to_py_content(temp_notebook):
    _, notebook_path, _ = temp_notebook

    # Call the conversion function
    result = convert_ipynb_to_py_content(notebook_path)

    # Check if the conversion includes the right content
    assert "# Generated from" in result
    assert "def hello_world():" in result
    assert "print(\"Hello, world!\")" in result
    assert "import numpy as np" in result
    assert "data = np.array([1, 2, 3])" in result

    # Ensure markdown content is not included
    assert "This is a markdown cell" not in result


def test_print_tree_with_ipynb_conversion(temp_notebook, monkeypatch):
    temp_dir, notebook_path, config_path = temp_notebook

    # Mock stdout and clipboard
    stdout_buffer = StringIO()
    clipboard_buffer = StringIO()
    monkeypatch.setattr("sys.stdout", stdout_buffer)
    monkeypatch.setattr(pyperclip, "copy", lambda x: clipboard_buffer.write(x))

    # Run the function
    print_tree_and_file_contents(config_path, to_clipboard=True)

    # Get the output content
    stdout_content = stdout_buffer.getvalue()
    clipboard_content = clipboard_buffer.getvalue()

    # Check that notebook content was processed properly
    for content in [stdout_content, clipboard_content]:
        assert f"File: {notebook_path}" in content
        assert "def hello_world():" in content
        assert "print(\"Hello, world!\")" in content
        assert "import numpy as np" in content
        # Check that markdown cells are not included
        assert "This is a markdown cell" not in content


def test_regex_file_with_ipynb_conversion(temp_notebook, monkeypatch):
    temp_dir, notebook_path, _ = temp_notebook

    # Create a new config with regexfiles
    regex_config = {
        "dirs": [],
        "files": [],
        "regexfiles": [
            {"dir": temp_dir, "pattern": ".*\\.ipynb$", "subdirs": True}
        ]
    }

    # Save the new config
    regex_config_path = os.path.join(temp_dir, "regex_config.yml")
    with open(regex_config_path, "w") as f:
        f.write(yaml.dump(regex_config))

    # Mock stdout and clipboard
    stdout_buffer = StringIO()
    clipboard_buffer = StringIO()
    monkeypatch.setattr("sys.stdout", stdout_buffer)
    monkeypatch.setattr(pyperclip, "copy", lambda x: clipboard_buffer.write(x))

    # Run the function with regex config
    print_tree_and_file_contents(regex_config_path, to_clipboard=True)

    # Get the output content
    stdout_content = stdout_buffer.getvalue()
    clipboard_content = clipboard_buffer.getvalue()

    # Check that notebook content was processed properly
    for content in [stdout_content, clipboard_content]:
        assert f"File: {notebook_path}" in content
        assert "def hello_world():" in content
        assert "import numpy as np" in content
        assert "This is a markdown cell" not in content
