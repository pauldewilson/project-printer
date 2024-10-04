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
    os.makedirs(os.path.join(temp_dir, "subdir", "nested_subdir"))

    file_paths = {
        "root_file.txt": os.path.join(temp_dir, "root_file.txt"),
        "subdir_file.txt": os.path.join(temp_dir, "subdir", "subdir_file.txt"),
        "nested_subdir_file.py": os.path.join(temp_dir, "subdir", "nested_subdir", "nested_file.py"),
        "init_file.py": os.path.join(temp_dir, "__init__.py"),
        "subdir_init_file.py": os.path.join(temp_dir, "subdir", "__init__.py"),
        "template.yml": os.path.join(temp_dir, "template.yml"),
        ".gitignore": os.path.join(temp_dir, ".gitignore")
    }

    # Create files with content
    with open(file_paths["root_file.txt"], "w") as f:
        f.write("This is the root file.")

    with open(file_paths["subdir_file.txt"], "w") as f:
        f.write("This is the file in a subdirectory.")

    with open(file_paths["nested_subdir_file.py"], "w") as f:
        f.write("print('This is a nested Python file.')")

    with open(file_paths["init_file.py"], "w") as f:
        f.write("# Root __init__.py")

    with open(file_paths["subdir_init_file.py"], "w") as f:
        f.write("# Subdir __init__.py")

    with open(file_paths["template.yml"], "w") as f:
        f.write("dirs:\n  - {}\nfiles:\n  - {}\ngitignore: {}\n".format(
            temp_dir, file_paths["root_file.txt"], file_paths[".gitignore"]
        ))

    with open(file_paths[".gitignore"], "w") as f:
        f.write("*.txt\n!root_file.txt\n")

    yield temp_dir, file_paths

    # Clean up the temporary directory
    shutil.rmtree(temp_dir)

# New tests for regexfiles and subdirs functionality

def test_regexfiles_subdirs_true(temp_dir_structure, monkeypatch):
    temp_dir, file_paths = temp_dir_structure

    # Create a configuration that uses regexfiles with subdirs: true
    config = {
        'dirs': [temp_dir],
        'files': [file_paths["root_file.txt"]],
        'regexfiles': [
            {
                'dir': temp_dir,
                'pattern': r'^.*\.py$',
                'subdirs': True
            }
        ],
        'gitignore': file_paths[".gitignore"]
    }

    # Write the configuration to the template.yml
    with open(file_paths["template.yml"], "w") as f:
        yaml.dump(config, f)

    # Capture the output
    output = StringIO()
    monkeypatch.setattr("sys.stdout", output)

    # Run the function
    print_tree_and_file_contents(file_paths["template.yml"], to_clipboard=False, dir_only=False)

    output_value = output.getvalue()

    # Check that all .py files are included, including in subdirectories
    assert "File: {}".format(file_paths["init_file.py"]) in output_value
    assert "# Root __init__.py" in output_value
    assert "File: {}".format(file_paths["subdir_init_file.py"]) in output_value
    assert "# Subdir __init__.py" in output_value
    assert "File: {}".format(file_paths["nested_subdir_file.py"]) in output_value
    assert "print('This is a nested Python file.')" in output_value

def test_regexfiles_subdirs_false(temp_dir_structure, monkeypatch):
    temp_dir, file_paths = temp_dir_structure

    # Create a configuration that uses regexfiles with subdirs: false
    config = {
        'dirs': [temp_dir],
        'files': [file_paths["root_file.txt"]],
        'regexfiles': [
            {
                'dir': temp_dir,
                'pattern': r'^.*\.py$',
                'subdirs': False
            }
        ],
        'gitignore': file_paths[".gitignore"]
    }

    # Write the configuration to the template.yml
    with open(file_paths["template.yml"], "w") as f:
        yaml.dump(config, f)

    # Capture the output
    output = StringIO()
    monkeypatch.setattr("sys.stdout", output)

    # Run the function
    print_tree_and_file_contents(file_paths["template.yml"], to_clipboard=False, dir_only=False)

    output_value = output.getvalue()

    # Check that only .py files in the root directory are included
    assert "File: {}".format(file_paths["init_file.py"]) in output_value
    assert "# Root __init__.py" in output_value
    # Files in subdirectories should not be included
    assert "File: {}".format(file_paths["subdir_init_file.py"]) not in output_value
    assert "File: {}".format(file_paths["nested_subdir_file.py"]) not in output_value

def test_regexfiles_exclude_init_py(temp_dir_structure, monkeypatch):
    temp_dir, file_paths = temp_dir_structure

    # Create a configuration that excludes __init__.py files
    config = {
        'dirs': [temp_dir],
        'files': [file_paths["root_file.txt"]],
        'regexfiles': [
            {
                'dir': temp_dir,
                'pattern': r'^(?!__init__\.py$).*\.py$',
                'subdirs': True
            }
        ],
        'gitignore': file_paths[".gitignore"]
    }

    # Write the configuration to the template.yml
    with open(file_paths["template.yml"], "w") as f:
        yaml.dump(config, f)

    # Capture the output
    output = StringIO()
    monkeypatch.setattr("sys.stdout", output)

    # Run the function
    print_tree_and_file_contents(file_paths["template.yml"], to_clipboard=False, dir_only=False)

    output_value = output.getvalue()

    # __init__.py files should not be included
    assert "File: {}".format(file_paths["init_file.py"]) not in output_value
    assert "File: {}".format(file_paths["subdir_init_file.py"]) not in output_value
    # Other .py files should be included
    assert "File: {}".format(file_paths["nested_subdir_file.py"]) in output_value
    assert "print('This is a nested Python file.')" in output_value

def test_regexfiles_invalid_pattern(temp_dir_structure, monkeypatch):
    temp_dir, file_paths = temp_dir_structure

    # Create a configuration with an invalid regex pattern
    config = {
        'dirs': [temp_dir],
        'files': [file_paths["root_file.txt"]],
        'regexfiles': [
            {
                'dir': temp_dir,
                'pattern': r'[invalid_regex',
                'subdirs': True
            }
        ],
        'gitignore': file_paths[".gitignore"]
    }

    # Write the configuration to the template.yml
    with open(file_paths["template.yml"], "w") as f:
        yaml.dump(config, f)

    # Capture the output
    output = StringIO()
    monkeypatch.setattr("sys.stdout", output)

    # Run the function
    print_tree_and_file_contents(file_paths["template.yml"], to_clipboard=False, dir_only=False)

    output_value = output.getvalue()

    # Check that an error message is displayed
    assert "Invalid regex pattern" in output_value

def test_regexfiles_no_dir_or_pattern(temp_dir_structure, monkeypatch):
    temp_dir, file_paths = temp_dir_structure

    # Create a configuration missing 'dir' and 'pattern' keys
    config = {
        'dirs': [temp_dir],
        'files': [file_paths["root_file.txt"]],
        'regexfiles': [
            {
                'subdirs': True
            }
        ],
        'gitignore': file_paths[".gitignore"]
    }

    # Write the configuration to the template.yml
    with open(file_paths["template.yml"], "w") as f:
        yaml.dump(config, f)

    # Capture the output
    output = StringIO()
    monkeypatch.setattr("sys.stdout", output)

    # Run the function
    print_tree_and_file_contents(file_paths["template.yml"], to_clipboard=False, dir_only=False)

    output_value = output.getvalue()

    # The entry should be skipped without errors
    assert "Base directory not found" not in output_value
    assert "Invalid regex pattern" not in output_value
    assert "Directory: {}".format(temp_dir) in output_value
    assert "File: {}".format(file_paths["root_file.txt"]) in output_value

def test_regexfiles_gitignore_exclusion(temp_dir_structure, monkeypatch):
    temp_dir, file_paths = temp_dir_structure

    # Update .gitignore to exclude nested_subdir_file.py
    with open(file_paths[".gitignore"], "a") as f:
        f.write("\nnested_file.py\n")

    # Create a configuration that includes nested_subdir_file.py
    config = {
        'dirs': [temp_dir],
        'files': [],
        'regexfiles': [
            {
                'dir': temp_dir,
                'pattern': r'^.*\.py$',
                'subdirs': True
            }
        ],
        'gitignore': file_paths[".gitignore"]
    }

    # Write the configuration to the template.yml
    with open(file_paths["template.yml"], "w") as f:
        yaml.dump(config, f)

    # Capture the output
    output = StringIO()
    monkeypatch.setattr("sys.stdout", output)

    # Run the function
    print_tree_and_file_contents(file_paths["template.yml"], to_clipboard=False, dir_only=False)

    output_value = output.getvalue()

    # nested_subdir_file.py should be excluded due to .gitignore
    assert "File: {}".format(file_paths["nested_subdir_file.py"]) not in output_value

def test_regexfiles_multiple_entries(temp_dir_structure, monkeypatch):
    temp_dir, file_paths = temp_dir_structure

    # Create additional files in another subdirectory
    os.makedirs(os.path.join(temp_dir, "another_subdir"))
    another_py_file = os.path.join(temp_dir, "another_subdir", "another_file.py")
    with open(another_py_file, "w") as f:
        f.write("print('Another Python file.')")

    # Create a configuration with multiple regexfiles entries
    config = {
        'dirs': [temp_dir],
        'files': [],
        'regexfiles': [
            {
                'dir': os.path.join(temp_dir, "subdir"),
                'pattern': r'^.*\.py$',
                'subdirs': True
            },
            {
                'dir': os.path.join(temp_dir, "another_subdir"),
                'pattern': r'^.*\.py$',
                'subdirs': False
            }
        ],
        'gitignore': file_paths[".gitignore"]
    }

    # Write the configuration to the template.yml
    with open(file_paths["template.yml"], "w") as f:
        yaml.dump(config, f)

    # Capture the output
    output = StringIO()
    monkeypatch.setattr("sys.stdout", output)

    # Run the function
    print_tree_and_file_contents(file_paths["template.yml"], to_clipboard=False, dir_only=False)

    output_value = output.getvalue()

    # Check that files are included as per the configuration
    assert "File: {}".format(file_paths["subdir_init_file.py"]) in output_value
    assert "File: {}".format(file_paths["nested_subdir_file.py"]) in output_value
    assert "File: {}".format(another_py_file) in output_value
    assert "Another Python file." in output_value

def test_regexfiles_files_not_found(temp_dir_structure, monkeypatch):
    temp_dir, file_paths = temp_dir_structure

    # Add a non-existent regexfiles entry
    non_existent_dir = os.path.join(temp_dir, "non_existent_dir")

    # Create a configuration with the non-existent directory
    config = {
        'dirs': [temp_dir],
        'files': [],
        'regexfiles': [
            {
                'dir': non_existent_dir,
                'pattern': r'^.*\.py$',
                'subdirs': True
            }
        ],
        'gitignore': file_paths[".gitignore"]
    }

    # Write the configuration to the template.yml
    with open(file_paths["template.yml"], "w") as f:
        yaml.dump(config, f)

    # Capture the output
    output = StringIO()
    monkeypatch.setattr("sys.stdout", output)

    # Run the function
    print_tree_and_file_contents(file_paths["template.yml"], to_clipboard=False, dir_only=False)

    output_value = output.getvalue()

    # Check that a message is displayed for the non-existent directory
    assert "Base directory not found: {}".format(non_existent_dir) in output_value

def test_regexfiles_dironly_option(temp_dir_structure, monkeypatch):
    temp_dir, file_paths = temp_dir_structure

    # Create a configuration with some files
    config = {
        'dirs': [temp_dir],
        'files': [file_paths["root_file.txt"]],
        'regexfiles': [
            {
                'dir': temp_dir,
                'pattern': r'^.*\.py$',
                'subdirs': True
            }
        ],
        'gitignore': file_paths[".gitignore"]
    }

    # Write the configuration to the template.yml
    with open(file_paths["template.yml"], "w") as f:
        yaml.dump(config, f)

    # Capture the output
    output = StringIO()
    monkeypatch.setattr("sys.stdout", output)

    # Run the function with dir_only=True
    print_tree_and_file_contents(file_paths["template.yml"], to_clipboard=False, dir_only=True)

    output_value = output.getvalue()

    # Check that file contents are not printed
    assert "File:" not in output_value
    assert "This is the root file." not in output_value
    assert "print('This is a nested Python file.')" not in output_value

    # Directory structure should still be printed
    assert "Directory: {}".format(temp_dir) in output_value
    assert "    +---root_file.txt" in output_value
    assert "    +---subdir" in output_value

def test_regexfiles_clipboard_option(temp_dir_structure, monkeypatch):
    temp_dir, file_paths = temp_dir_structure

    # Create a configuration with some files
    config = {
        'dirs': [temp_dir],
        'files': [file_paths["root_file.txt"]],
        'regexfiles': [],
        'gitignore': file_paths[".gitignore"]
    }

    # Write the configuration to the template.yml
    with open(file_paths["template.yml"], "w") as f:
        yaml.dump(config, f)

    # Mock pyperclip
    clipboard_content = StringIO()
    monkeypatch.setattr(pyperclip, "copy", lambda x: clipboard_content.write(x))

    # Run the function with to_clipboard=True
    print_tree_and_file_contents(file_paths["template.yml"], to_clipboard=True, dir_only=False)

    # Check if the output was copied to the clipboard
    clipboard_value = clipboard_content.getvalue()
    assert "Directory: {}".format(temp_dir) in clipboard_value
    assert "File: {}".format(file_paths["root_file.txt"]) in clipboard_value
    assert "This is the root file." in clipboard_value
