import re
import os
import sys
try:
    import pyperclip
    CLIPBOARD_AVAILABLE = True
except ImportError:
    CLIPBOARD_AVAILABLE = False

def parse_directory_structure(input_text, path_type='both', file_pattern=None):
    """
    Parse a directory structure text and extract filepaths matching criteria.

    Args:
        input_text (str): Text representation of the directory structure
        path_type (str): Type of paths to return: 'files', 'dirs', or 'both'
        file_pattern (str, optional): Regex pattern to match specific files. Default None matches all files.

    Returns:
        list: List of full filepaths
    """
    # Check if input is already in list format (without +---)
    if not input_text.strip().startswith('Directory:') and not input_text.find('+---') >= 0:
        # Assume the input is already a list of paths
        paths = [line.strip() for line in input_text.splitlines() if line.strip()]

        # Apply proper Windows path formatting
        paths = [fix_windows_path(p) for p in paths]

        # Filter by type if needed
        if path_type == 'files':
            # No extension means directory in most file systems
            return [p for p in paths if '.' in os.path.basename(p)]
        elif path_type == 'dirs':
            # This is an approximation, may need refinement
            return [p for p in paths if '.' not in os.path.basename(p)]
        else:
            return paths

    # Process directory tree format (with +---)
    # First, determine the base directory
    base_dir_match = re.search(r'Directory: (.*?)$', input_text, re.MULTILINE)
    if not base_dir_match:
        raise ValueError("Cannot find base directory in the input text")

    base_dir = base_dir_match.group(1).strip()

    # Get the first directory name which will be a duplicate in the paths
    first_dir_match = re.search(r'\+---([^\n\r]+)', input_text)
    if not first_dir_match:
        raise ValueError("Cannot find the first directory in the structure")

    first_dir = first_dir_match.group(1).strip()

    # Parse the directory structure
    # We'll transform the +--- structure into a list of paths
    lines = input_text.splitlines()
    current_path = []
    paths = []

    for line in lines:
        # Skip the base directory line and empty lines
        if line.startswith('Directory:') or not line.strip():
            continue

        # Count the indentation level by counting the number of spaces before +---
        indent = line.find('+---')
        if indent == -1:
            continue

        # Normalize indent to path depth
        depth = indent // 4

        # If current path is deeper than current line, pop elements
        while len(current_path) > depth:
            current_path.pop()

        # Extract the name (remove +---)
        name = line[indent + 4:].strip()

        # Update current path with new item
        if len(current_path) == depth:
            current_path.append(name)
        else:
            current_path[depth] = name

        # Check if it matches the requested type
        is_file = '.' in name  # Simple heuristic: if it has an extension, it's a file

        if (path_type == 'both' or
            (path_type == 'files' and is_file) or
            (path_type == 'dirs' and not is_file)):

            # If a file pattern is specified and this is a file
            if file_pattern and is_file:
                if re.search(file_pattern, name):
                    paths.append(os.path.join(base_dir, *current_path))
            elif file_pattern is None or not is_file:
                paths.append(os.path.join(base_dir, *current_path))

    # Remove the duplicate directory from paths to match expected format
    fixed_paths = []
    for path in paths:
        parts = path.split(os.sep)
        if parts.count(first_dir) > 1:
            # Find the second occurrence of the first_dir
            duplicate_index = -1
            found_first = False
            for i, part in enumerate(parts):
                if part == first_dir:
                    if found_first:
                        duplicate_index = i
                        break
                    found_first = True

            if duplicate_index != -1:
                # Remove the duplicate directory
                new_parts = parts[:duplicate_index] + parts[duplicate_index+1:]
                fixed_paths.append(os.path.join(*new_parts))
        else:
            fixed_paths.append(path)

    # Fix Windows paths
    fixed_paths = [fix_windows_path(p) for p in fixed_paths]

    return fixed_paths

def fix_windows_path(path):
    """
    Ensure Windows paths have proper backslash after drive letter.

    Args:
        path (str): A file path

    Returns:
        str: Properly formatted path
    """
    # Check if this is a Windows path starting with a drive letter (e.g., C:)
    if re.match(r'^[A-Za-z]:', path):
        # Add backslash after drive letter if missing
        if len(path) > 2 and path[2] != '\\':
            path = path[:2] + '\\' + path[2:]
    return path

def format_as_yaml(filepaths):
    """
    Format a list of filepaths as YAML-style output.

    Args:
        filepaths (list): List of filepaths

    Returns:
        str: YAML-formatted string
    """
    # Ensure proper backslashes in Windows paths
    formatted_paths = []
    for path in filepaths:
        path = fix_windows_path(path)
        formatted_paths.append(f"  - {path}")

    return "\n".join(formatted_paths)

def get_paths_with_pattern(input_text, path_type='both', pattern=None):
    """
    Get paths from the directory structure based on type and pattern.

    Args:
        input_text (str): Text representation of the directory structure
        path_type (str): Type of paths to return: 'files', 'dirs', or 'both'
        pattern (str, optional): Regex pattern to match specific files

    Returns:
        str: YAML-formatted list of matching paths
    """
    paths = parse_directory_structure(input_text, path_type, pattern)
    return format_as_yaml(paths)

def get_readme_paths(input_text, path_type='files'):
    """
    Get all README.md filepaths from the directory structure.

    Args:
        input_text (str): Text representation of the directory structure
        path_type (str): Type of paths to return: 'files', 'dirs', or 'both'

    Returns:
        str: YAML-formatted list of README.md filepaths
    """
    return get_paths_with_pattern(input_text, path_type, r'README\.md$')

def get_all_paths(input_text, path_type='both'):
    """
    Get all paths from the directory structure.

    Args:
        input_text (str): Text representation of the directory structure
        path_type (str): Type of paths to return: 'files', 'dirs', or 'both'

    Returns:
        str: YAML-formatted list of all paths
    """
    return get_paths_with_pattern(input_text, path_type)

def interactive_menu():
    """
    Display an interactive menu for the user to choose options.

    Returns:
        tuple: (path_type, pattern)
    """
    print("\nSelect path type to include:")
    print("1. Files only")
    print("2. Directories only")
    print("3. Both files and directories (default)")

    choice = input("Enter your choice (1-3) [3]: ").strip()
    if not choice:
        choice = "3"  # Default

    if choice == "1":
        path_type = "files"
    elif choice == "2":
        path_type = "dirs"
    else:
        path_type = "both"

    print("\nDo you want to filter by a pattern?")
    print("1. No filter (show all paths)")
    print("2. README.md files only")
    print("3. Custom pattern")

    choice = input("Enter your choice (1-3) [1]: ").strip()
    if not choice:
        choice = "1"  # Default

    if choice == "1":
        pattern = None
    elif choice == "2":
        pattern = r'README\.md$'
    elif choice == "3":
        pattern = input("Enter regex pattern (e.g. '.py$' for Python files): ").strip()
    else:
        pattern = None

    return path_type, pattern

def main():
    """Main function to run the script."""
    import sys

    print("Directory Structure Parser")
    print("=========================")
    print("This script parses directory structures and outputs paths in YAML format.")

    if len(sys.argv) > 1:
        input_file = sys.argv[1]
        try:
            with open(input_file, 'r') as f:
                directory_structure = f.read()
            print(f"Read input from file: {input_file}")
        except Exception as e:
            print(f"Error reading file: {e}")
            return
    else:
        # Get from stdin if no file is specified
        print("\nEnter or paste your directory structure below.")
        print("When finished, type 'END' on a new line and press Enter.")
        print("------------------------------------------------------------------")

        try:
            directory_structure = ""
            line = ""
            while True:
                try:
                    line = input()
                    if line.strip() == "END":
                        break
                    directory_structure += line + "\n"
                except EOFError:
                    break
        except KeyboardInterrupt:
            print("\nOperation cancelled by user.")
            return

    if not directory_structure.strip():
        print("No input provided. Exiting.")
        return

    try:
        path_type, pattern = interactive_menu()

        result = get_paths_with_pattern(directory_structure, path_type, pattern)

        print("\nMatching paths:")
        print(result)

        # Optionally save to file or copy to clipboard
        save_choice = input("\nDo you want to save the output to a file? (y/n) [n]: ").strip().lower()
        if save_choice == 'y':
            output_file = input("Enter output filename [output.yml]: ").strip()
            if not output_file:
                output_file = "output.yml"

            with open(output_file, 'w') as f:
                f.write(result)
            print(f"Output saved to {output_file}")

        # Offer clipboard option if available
        if CLIPBOARD_AVAILABLE:
            clipboard_choice = input("\nDo you want to copy the output to clipboard? (y/n) [n]: ").strip().lower()
            if clipboard_choice == 'y':
                try:
                    pyperclip.copy(result)
                    print("Output copied to clipboard successfully!")
                except Exception as e:
                    print(f"Error copying to clipboard: {e}")
        else:
            print("\nNote: Clipboard functionality not available. Install pyperclip with 'pip install pyperclip' to enable.")

    except Exception as e:
        print(f"Error processing directory structure: {e}")

if __name__ == "__main__":
    main()