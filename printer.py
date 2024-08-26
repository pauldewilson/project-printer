import os
import subprocess
import yaml
import argparse
import pyperclip
from io import StringIO
from pathspec import PathSpec

# ANSI escape codes for colors
COLOR_CODES = {
    'reset': '\033[0m',
    'green': '\033[92m',
    'blue': '\033[94m',
    'default': ''
}

def color_output(output, color):
    """Wraps the output string in ANSI color codes."""
    return f"{COLOR_CODES.get(color, '')}{output}{COLOR_CODES['reset']}"

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

def get_tree_output(dir_path, spec):
    """Returns the directory tree as a list, excluding paths matching gitignore patterns."""
    tree = []
    for root, dirs, files in os.walk(dir_path):
        # Filter directories and files based on gitignore patterns
        dirs[:] = [d for d in dirs if not spec.match_file(os.path.relpath(os.path.join(root, d), dir_path))]
        files = [f for f in files if not spec.match_file(os.path.relpath(os.path.join(root, f), dir_path))]

        # Append the current directory
        level = os.path.relpath(root, dir_path).count(os.sep)
        indent = '    ' * level
        if level == 0:
            tree.append(f"{indent}{os.path.basename(root)}")  # Root directory
        else:
            tree.append(f"{indent}+---{os.path.basename(root)}")  # Subdirectories

        # Append files in the current directory
        for file in files:
            file_indent = '    ' * (level + 1)
            tree.append(f"{file_indent}+---{file}")
    return tree

def print_tree_and_file_contents(config_file, to_clipboard=False, dir_only=False):
    # Load the YAML configuration
    with open(config_file, 'r') as file:
        config = yaml.safe_load(file)

    dirs = config.get('dirs', [])
    files = config.get('files', [])
    gitignore_path = config.get('gitignore')

    # Load gitignore patterns
    spec = load_gitignore_patterns(gitignore_path) if gitignore_path else PathSpec.from_lines('gitwildmatch', [])

    output = StringIO()
    printed_files = set()

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

            # Skip printing file contents if dir_only is True
            if not dir_only:
                for file_path in files:
                    normalized_file_path = os.path.normpath(file_path)
                    rel_path = os.path.relpath(normalized_file_path, dir_path)

                    if os.path.exists(normalized_file_path) and not spec.match_file(rel_path) and normalized_file_path not in printed_files:
                        output.write(f"\nFile: {normalized_file_path}\n")
                        output.write('```\n')
                        with open(normalized_file_path, 'r', encoding='utf-8') as f:
                            output.write(f.read())
                        output.write('\n```\n')
                        printed_files.add(normalized_file_path)
                        print(f"\nFile: {normalized_file_path}")
                        print('```')
                        with open(normalized_file_path, 'r', encoding='utf-8') as f:
                            print(f.read())
                        print('```')
        else:
            output.write(f"\nDirectory not found: {dir_path}\n")
            print(f"\nDirectory not found: {dir_path}")

    # Check for files not found or ignored
    if not dir_only:
        unfound_files = [f for f in files if f not in printed_files]
        if unfound_files:
            output.write("\nFiles not found or ignored:\n")
            for unfound_file in unfound_files:
                output.write(f"{unfound_file}\n")
                print(f"{unfound_file}")

    final_output = output.getvalue().strip()

    if to_clipboard:
        pyperclip.copy(final_output)
        print(color_output("\nOutput has been copied to the clipboard.", 'green'))

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Print directory tree and file contents with gitignore support.")
    parser.add_argument("--config", default="proj.yml", help="Path to the YAML configuration file.")
    parser.add_argument("--clipboard", action="store_true", help="Copy output to clipboard.")
    parser.add_argument("--dironly", action="store_true", help="Print only the directory structure, no file contents.")
    args = parser.parse_args()

    print_tree_and_file_contents(args.config, to_clipboard=args.clipboard, dir_only=args.dironly)
