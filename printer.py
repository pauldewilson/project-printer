import os
import yaml
import argparse
import pyperclip
import re
import sys
import json
from io import StringIO
from pathspec import PathSpec

# ANSI escape codes for colors
COLOR_CODES = {
    'reset': '\033[0m',
    'green': '\033[92m',
    'blue': '\033[94m',
    'red': '\033[91m',
    'default': ''
}

def color_output(output, color_name):
    """Wraps the output string in ANSI color codes if output is to a terminal."""
    if sys.stdout.isatty():
        return f"{COLOR_CODES.get(color_name, '')}{output}{COLOR_CODES['reset']}"
    else:
        return output

def load_gitignore_patterns(gitignore_path):
    """Load gitignore patterns from the specified file."""
    try:
        with open(gitignore_path, 'r') as gitignore_file:
            patterns = gitignore_file.read().splitlines()
            spec = PathSpec.from_lines('gitwildmatch', patterns)
            return spec
    except FileNotFoundError:
        print(f".gitignore file not found at: {gitignore_path}")
        return PathSpec.from_lines('gitwildmatch', [])

def is_excluded(path, spec, is_dir=False):
    """Check if a path is excluded by the gitignore patterns."""
    if is_dir and not path.endswith('/'):
        path += '/'
    return spec.match_file(path)

def get_tree_output(dir_path, spec):
    """Returns the directory tree as a list, excluding paths matching gitignore patterns."""
    tree = []
    for root, dirs, files in os.walk(dir_path):
        rel_root = os.path.relpath(root, dir_path)
        if rel_root == '.':
            rel_root = ''
            level = 0
        else:
            level = rel_root.count(os.sep) + 1  # Adjust level for proper indentation

        indent = '    ' * level
        # Always use '+---' for subdirectories, including immediate subdirectories
        tree.append(f"{indent}+---{os.path.basename(root)}")

        # Filter directories and files based on gitignore patterns
        dirs[:] = [d for d in dirs if not is_excluded(os.path.join(rel_root, d), spec, is_dir=True)]
        files = [f for f in files if not is_excluded(os.path.join(rel_root, f), spec, is_dir=False)]

        # Append files in the current directory
        for file in files:
            file_indent = '    ' * (level + 1)
            tree.append(f"{file_indent}+---{file}")
    return tree

def convert_ipynb_to_py_content(ipynb_path):
    """Converts an ipynb file to python code and returns the content as a string."""
    try:
        with open(ipynb_path, 'r', encoding='utf-8') as f:
            notebook = json.load(f)

        output = StringIO()
        output.write(f"# Generated from {ipynb_path}\n\n")

        # Extract and write all code cells
        for cell in notebook['cells']:
            if cell['cell_type'] == 'code':
                # Get the source code lines
                source = cell.get('source', [])
                if isinstance(source, list):
                    code = ''.join(source)
                else:
                    code = source

                # Skip empty cells
                if not code.strip():
                    continue

                # Write the code with a separator for readability
                output.write(f"{code}\n\n")

        return output.getvalue()
    except Exception as e:
        return f"Error converting notebook: {str(e)}"

def print_tree_and_file_contents(config_file, to_clipboard=False, dir_only=False, no_dirtree=False):
    # Load the YAML configuration
    with open(config_file, 'r') as file:
        config = yaml.safe_load(file)

    # Add a list to store not found directories and files
    not_found = []

    dirs = config.get('dirs', [])
    files = config.get('files', [])
    regex_files = config.get('regexfiles', [])
    gitignore_path = config.get('gitignore')

    # Load gitignore patterns
    spec = load_gitignore_patterns(gitignore_path) if gitignore_path else PathSpec.from_lines('gitwildmatch', [])

    output = StringIO()
    printed_files = set()


    if no_dirtree:
        pass
    else:
        for dir_path in dirs:
            dir_path = os.path.normpath(dir_path)

            if os.path.exists(dir_path):
                tree_output = get_tree_output(dir_path, spec)
                # Generate non-colored output for clipboard
                output.write(f"\nDirectory: {dir_path}\n")
                for line in tree_output:
                    output.write(line + "\n")

                # Print colored output to terminal
                print(color_output(f"\nDirectory: {dir_path}\n", 'blue'))
                for line in tree_output:
                    print(color_output(line, 'blue'))

            else:
                not_found.append(f"Directory not found: {dir_path}")
                output.write(f"\nDirectory not found: {dir_path}\n")

    if not dir_only:
        # Process files specified under 'files'
        for file_path in files:
            normalized_file_path = os.path.normpath(file_path)

            if os.path.exists(normalized_file_path) and normalized_file_path not in printed_files:
                # Check if file is excluded by gitignore patterns
                rel_path = os.path.relpath(normalized_file_path)
                if not is_excluded(rel_path, spec, is_dir=False):
                    output.write(f"\nFile: {normalized_file_path}\n")
                    output.write('```\n')

                    # Check if the file is a Jupyter notebook
                    if normalized_file_path.endswith('.ipynb'):
                        content = convert_ipynb_to_py_content(normalized_file_path)
                    else:
                        try:
                            with open(normalized_file_path, 'r', encoding='utf-8') as f:
                                content = f.read()
                        except UnicodeDecodeError:
                            with open(normalized_file_path, 'r', encoding='latin-1') as f:
                                content = f.read()

                    output.write(content)
                    output.write('\n```\n')
                    printed_files.add(normalized_file_path)
                    print(f"\nFile: {normalized_file_path}")
                    print('```\n')
                    print(content)
                    print('\n```\n')
                else:
                    not_found.append(f"File excluded by gitignore: {normalized_file_path}")
                    output.write(f"\nFile excluded by gitignore: {normalized_file_path}\n")
            else:
                not_found.append(f"File not found: {normalized_file_path}")
                output.write(f"\nFile not found: {normalized_file_path}\n")

        # Process regex files
        for regex_entry in regex_files:
            base_dir = regex_entry.get('dir')
            pattern = regex_entry.get('pattern')
            subdirs = regex_entry.get('subdirs', True)  # Default to True

            if not base_dir or not pattern:
                continue  # Skip invalid entries

            base_dir = os.path.normpath(base_dir)
            if not os.path.exists(base_dir):
                not_found.append(f"Base directory not found: {base_dir}")
                output.write(f"\nBase directory not found: {base_dir}\n")
                continue

            # Compile the regex pattern
            try:
                regex_compiled = re.compile(pattern)
            except re.error as e:
                not_found.append(f"Invalid regex pattern '{pattern}': {e}")
                output.write(f"\nInvalid regex pattern '{pattern}': {e}\n")
                continue

            if subdirs:
                # Walk through the base directory and find matching files
                for root, dirs, files_in_dir in os.walk(base_dir):
                    rel_root = os.path.relpath(root, base_dir)
                    if rel_root == '.':
                        rel_root = ''

                    # Filter directories based on gitignore patterns
                    dirs[:] = [d for d in dirs if not is_excluded(os.path.join(rel_root, d), spec, is_dir=True)]

                    for file_name in files_in_dir:
                        file_path = os.path.join(root, file_name)
                        rel_path = os.path.relpath(file_path, base_dir)

                        if is_excluded(rel_path, spec, is_dir=False):
                            continue  # Exclude files matching gitignore patterns

                        if file_path in printed_files:
                            continue  # Skip files already printed

                        if regex_compiled.search(file_name):
                            # Process the file content
                            if file_path.endswith('.ipynb'):
                                content = convert_ipynb_to_py_content(file_path)
                            else:
                                # Read the file content
                                try:
                                    with open(file_path, 'r', encoding='utf-8') as f:
                                        content = f.read()
                                except UnicodeDecodeError:
                                    with open(file_path, 'r', encoding='latin-1') as f:
                                        content = f.read()

                            # Write to output buffer
                            output.write(f"\nFile: {file_path}\n")
                            output.write('```\n')
                            output.write(content)
                            output.write('\n```\n')
                            printed_files.add(file_path)
                            # Print to terminal
                            print(f"\nFile: {file_path}")
                            print('```\n')
                            print(content)
                            print('\n```\n')
            else:
                # Only process the specified directory
                try:
                    files_in_dir = [f for f in os.listdir(base_dir) if os.path.isfile(os.path.join(base_dir, f))]
                except Exception as e:
                    not_found.append(f"Error accessing directory '{base_dir}': {e}")
                    output.write(f"\nError accessing directory '{base_dir}': {e}\n")
                    continue

                for file_name in files_in_dir:
                    file_path = os.path.join(base_dir, file_name)
                    rel_path = os.path.relpath(file_path, base_dir)

                    if is_excluded(rel_path, spec, is_dir=False):
                        continue  # Exclude files matching gitignore patterns

                    if file_path in printed_files:
                        continue  # Skip files already printed

                    if regex_compiled.search(file_name):
                        # Process the file content
                        if file_path.endswith('.ipynb'):
                            content = convert_ipynb_to_py_content(file_path)
                        else:
                            # Read the file content
                            try:
                                with open(file_path, 'r', encoding='utf-8') as f:
                                    content = f.read()
                            except UnicodeDecodeError:
                                with open(file_path, 'r', encoding='latin-1') as f:
                                    content = f.read()

                        # Write to output buffer
                        output.write(f"\nFile: {file_path}\n")
                        output.write('```\n')
                        output.write(content)
                        output.write('\n```\n')
                        printed_files.add(file_path)
                        # Print to terminal
                        print(f"\nFile: {file_path}")
                        print('```\n')
                        print(content)
                        print('\n```\n')

    # At the end of the function, print all not found messages in red
    if not_found:
        print(color_output("\nFiles or directories not found:", 'red'))
        for nf in not_found:
            print(color_output(nf, 'red'))

    final_output = output.getvalue().strip()

    if to_clipboard:
        pyperclip.copy(final_output)
        print(color_output("\nOutput has been copied to the clipboard.", 'green'))

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Print directory tree and file contents with gitignore support.")
    parser.add_argument("--config", default="proj.yml", help="Path to the YAML configuration file.")
    parser.add_argument("--clipboard", action="store_true", help="Copy output to clipboard.")
    parser.add_argument("--dironly", action="store_true", help="Print only the directory structure, no file contents.")
    parser.add_argument("--nodirtree", action="store_true", help="Do not print directory structure.")
    args = parser.parse_args()

    print_tree_and_file_contents(args.config, to_clipboard=args.clipboard, dir_only=args.dironly, no_dirtree=args.nodirtree)