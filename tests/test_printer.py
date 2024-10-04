import os
import tempfile
import shutil
import pytest
import pyperclip
from io import StringIO
from printer import print_tree_and_file_contents, load_gitignore_patterns, get_tree_output
import yaml

@pytest.fixture
def temp_dir_structure():
    # Create a temporary directory
    temp_dir = tempfile.mkdtemp()

    # Create subdirectories and files
    os.makedirs(os.path.join(temp_dir, "subdir"))
    file_paths = {
        "root_file.txt": os.path.join(temp_dir, "root_file.txt"),
        "subdir_file.txt": os.path.join(temp_dir, "subdir", "subdir_file.txt"),
        "template.yml": os.path.join(temp_dir, "template.yml"),
        ".gitignore": os.path.join(temp_dir, ".gitignore")
    }

    with open(file_paths["root_file.txt"], "w") as f:
        f.write("This is the root file.")

    with open(file_paths["subdir_file.txt"], "w") as f:
        f.write("This is the file in a subdirectory.")

    with open(file_paths["template.yml"], "w") as f:
        f.write("dirs:\n  - {}\nfiles:\n  - {}\ngitignore: {}\n".format(
            temp_dir, file_paths["root_file.txt"], file_paths[".gitignore"]
        ))

    with open(file_paths[".gitignore"], "w") as f:
        f.write("*.txt\n!root_file.txt\n")

    yield temp_dir, file_paths

    # Clean up the temporary directory
    shutil.rmtree(temp_dir)

def test_print_tree_and_file_contents(temp_dir_structure, monkeypatch):
    temp_dir, file_paths = temp_dir_structure

    # Mock the configuration file path and pyperclip
    config_file = file_paths["template.yml"]
    clipboard_content = StringIO()
    monkeypatch.setattr(pyperclip, "copy", lambda x: clipboard_content.write(x))

    # Capture the output
    output = StringIO()
    monkeypatch.setattr("sys.stdout", output)

    # Run the function
    print_tree_and_file_contents(config_file, to_clipboard=True, dir_only=False)

    # Check if the directory structure is printed correctly
    output_value = output.getvalue()
    assert "Directory: {}".format(temp_dir) in output_value
    assert "    +---root_file.txt" in output_value
    assert "subdir" in output_value  # Adjusted to match the output format
    assert "File: {}".format(file_paths["root_file.txt"]) in output_value
    assert "This is the root file." in output_value

    # Check if the output was copied to the clipboard
    clipboard_value = clipboard_content.getvalue()
    assert "Directory: {}".format(temp_dir) in clipboard_value
    assert "    +---root_file.txt" in clipboard_value
    assert "subdir" in clipboard_value  # Adjusted to match the output format
    assert "File: {}".format(file_paths["root_file.txt"]) in clipboard_value
    assert "This is the root file." in clipboard_value

def test_gitignore_patterns(temp_dir_structure):
    temp_dir, file_paths = temp_dir_structure

    # Load the gitignore patterns
    spec = load_gitignore_patterns(file_paths[".gitignore"])

    # Check if the correct files are ignored
    assert not spec.match_file("root_file.txt")
    assert spec.match_file("subdir_file.txt")

def test_get_tree_output(temp_dir_structure):
    temp_dir, file_paths = temp_dir_structure

    # Load the gitignore patterns
    spec = load_gitignore_patterns(file_paths[".gitignore"])

    # Get the tree output
    tree_output = get_tree_output(temp_dir, spec)

    # Check if the directory structure is returned correctly
    assert "{}".format(os.path.basename(temp_dir)) in tree_output[0]
    assert "    +---root_file.txt" in tree_output  # Adjusted to match the output format
    assert "    +---subdir" in tree_output  # Adjusted to match the output format
    assert "+---subdir_file.txt" not in tree_output  # This should be ignored due to .gitignore
