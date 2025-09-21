"""
File and directory operations for the terminal.
"""
import os
import shutil
from typing import List, Tuple
from utils.helpers import normalize_path, is_safe_path, format_file_size, format_timestamp, get_file_permissions, is_safe_to_delete


def ls_command(cwd: str, args: List[str]) -> str:
    """
    List directory contents.

    Args:
        cwd (str): Current working directory
        args (List[str]): Command arguments

    Returns:
        str: Formatted directory listing
    """
    try:
        # Parse arguments
        show_hidden = False
        long_format = False
        target_dir = cwd

        for arg in args:
            if arg.startswith('-'):
                if 'a' in arg:
                    show_hidden = True
                if 'l' in arg:
                    long_format = True
            else:
                target_dir = arg

        # Normalize target directory
        target_path = normalize_path(target_dir, cwd)

        if not is_safe_path(target_path, cwd):
            return "Error: Access denied - path outside allowed directories"

        if not os.path.exists(target_path):
            return f"Error: Directory '{target_dir}' not found"

        if not os.path.isdir(target_path):
            return f"Error: '{target_dir}' is not a directory"

        # Get directory contents
        try:
            items = os.listdir(target_path)
        except PermissionError:
            return f"Error: Permission denied accessing '{target_dir}'"

        # Filter hidden files if not showing all
        if not show_hidden:
            items = [item for item in items if not item.startswith('.')]

        # Sort items (directories first, then files)
        items.sort(key=lambda x: (not os.path.isdir(
            os.path.join(target_path, x)), x.lower()))

        if not items:
            return f"Directory '{target_dir}' is empty"

        # Format output
        if long_format:
            return _format_long_listing(items, target_path)
        else:
            return _format_simple_listing(items)

    except Exception as e:
        return f"Error listing directory: {str(e)}"


def _format_long_listing(items: List[str], base_path: str) -> str:
    """Format directory listing in long format."""
    lines = []

    for item in items:
        item_path = os.path.join(base_path, item)
        try:
            stat_info = os.stat(item_path)

            # File type indicator
            if os.path.isdir(item_path):
                file_type = '[DIR]'
            elif os.path.islink(item_path):
                file_type = '[LINK]'
            else:
                file_type = '[FILE]'

            # Size
            size = format_file_size(stat_info.st_size)

            # Date modified
            date_modified = format_timestamp(stat_info.st_mtime)

            # Name (with link target if symlink)
            name = item
            if os.path.islink(item_path):
                try:
                    link_target = os.readlink(item_path)
                    name = f"{item} -> {link_target}"
                except OSError:
                    name = f"{item} -> (broken link)"

            lines.append(f"{file_type:>6} {size:>8} {date_modified} {name}")

        except (OSError, ValueError):
            lines.append(f"[ERR] {'':>8} {'':>19} {item} (error reading file)")

    return "\n".join(lines)


def _format_simple_listing(items: List[str]) -> str:
    """Format directory listing in simple format."""
    if not items:
        return ""

    # Simple, clean format - one item per line for better readability
    return "\n".join(items)


def cd_command(cwd: str, args: List[str]) -> Tuple[str, str]:
    """
    Change directory.

    Args:
        cwd (str): Current working directory
        args (List[str]): Command arguments

    Returns:
        Tuple[str, str]: (output_message, new_cwd)
    """
    try:
        if not args:
            # No arguments - go to home directory
            new_cwd = os.path.expanduser("~")
        else:
            target_dir = args[0]

            # Handle special cases
            if target_dir == "/" or target_dir == "\\":
                # Go to system root
                new_cwd = os.path.abspath(os.sep)
            elif target_dir == "..":
                # Go up one directory
                new_cwd = os.path.dirname(cwd)
            elif target_dir == ".":
                # Stay in current directory
                new_cwd = cwd
            else:
                new_cwd = normalize_path(target_dir, cwd)

        # Check if path is safe (more permissive)
        if not is_safe_path(new_cwd, cwd):
            # For root directory access, allow if it's just listing
            if new_cwd == os.path.abspath(os.sep):
                # Allow access to root for listing purposes
                pass
            else:
                return "Error: Access denied - path outside allowed directories", cwd

        if not os.path.exists(new_cwd):
            return f"Error: Directory '{target_dir}' not found", cwd

        if not os.path.isdir(new_cwd):
            return f"Error: '{target_dir}' is not a directory", cwd

        # IMPORTANT: Don't change the actual working directory with os.chdir()
        # This breaks Streamlit because it looks for app.py in the new directory
        # Instead, just return the new path for the terminal to track
        return "", new_cwd

    except PermissionError:
        return f"Error: Permission denied accessing '{target_dir}'", cwd
    except Exception as e:
        return f"Error changing directory: {str(e)}", cwd


def pwd_command(cwd: str, args: List[str]) -> str:
    """
    Print working directory.

    Args:
        cwd (str): Current working directory
        args (List[str]): Command arguments (ignored)

    Returns:
        str: Current working directory path
    """
    return cwd


def mkdir_command(cwd: str, args: List[str]) -> str:
    """
    Create directory.

    Args:
        cwd (str): Current working directory
        args (List[str]): Command arguments

    Returns:
        str: Success or error message
    """
    if not args:
        return "Error: mkdir requires a directory name"

    try:
        for dir_name in args:
            dir_path = normalize_path(dir_name, cwd)

            if not is_safe_path(dir_path, cwd):
                return f"Error: Access denied - path outside allowed directories"

            if os.path.exists(dir_path):
                return f"Error: Directory '{dir_name}' already exists"

            os.makedirs(dir_path, exist_ok=False)

        return f"Created directory(ies): {', '.join(args)}"

    except PermissionError:
        return f"Error: Permission denied creating directory '{args[0]}'"
    except FileExistsError:
        return f"Error: Directory '{args[0]}' already exists"
    except Exception as e:
        return f"Error creating directory: {str(e)}"


def rm_command(cwd: str, args: List[str]) -> str:
    """
    Remove file or directory.

    Args:
        cwd (str): Current working directory
        args (List[str]): Command arguments

    Returns:
        str: Success or error message
    """
    if not args:
        return "Error: rm requires a file or directory name"

    try:
        recursive = False
        items_to_remove = []

        # Parse arguments
        for arg in args:
            if arg.startswith('-'):
                if 'r' in arg or 'R' in arg:
                    recursive = True
            else:
                items_to_remove.append(arg)

        if not items_to_remove:
            return "Error: rm requires a file or directory name"

        removed_items = []

        for item_name in items_to_remove:
            item_path = normalize_path(item_name, cwd)

            if not is_safe_path(item_path, cwd):
                return f"Error: Access denied - path outside allowed directories"

            if not os.path.exists(item_path):
                return f"Error: '{item_name}' not found"

            # Enhanced safety check for Ubuntu system protection
            is_safe, reason = is_safe_to_delete(item_path)
            if not is_safe:
                return f"Error: Cannot remove '{item_name}' - {reason}"

            # Additional safety check - prevent dangerous operations
            if item_path in ['/', '\\', 'C:\\', '/home', '/root']:
                return f"Error: Cannot remove system directory '{item_name}'"

            try:
                if os.path.isdir(item_path):
                    if recursive:
                        shutil.rmtree(item_path)
                        removed_items.append(f"directory '{item_name}'")
                    else:
                        return f"Error: '{item_name}' is a directory (use -r for recursive removal)"
                else:
                    os.remove(item_path)
                    removed_items.append(f"file '{item_name}'")

            except PermissionError:
                return f"Error: Permission denied removing '{item_name}'"
            except OSError as e:
                return f"Error removing '{item_name}': {str(e)}"

        return f"Removed: {', '.join(removed_items)}"

    except Exception as e:
        return f"Error removing items: {str(e)}"


def rmdir_command(cwd: str, args: List[str]) -> str:
    """
    Remove empty directory (Windows style).

    Args:
        cwd (str): Current working directory
        args (List[str]): Command arguments

    Returns:
        str: Success or error message
    """
    if not args:
        return "Error: rmdir requires a directory name"

    try:
        removed_dirs = []

        for dir_name in args:
            dir_path = normalize_path(dir_name, cwd)

            if not is_safe_path(dir_path, cwd):
                return f"Error: Access denied - path outside allowed directories"

            if not os.path.exists(dir_path):
                return f"Error: Directory '{dir_name}' not found"

            if not os.path.isdir(dir_path):
                return f"Error: '{dir_name}' is not a directory"

            try:
                # Check if directory is empty
                if os.listdir(dir_path):
                    return f"Error: Directory '{dir_name}' is not empty"

                os.rmdir(dir_path)
                removed_dirs.append(f"directory '{dir_name}'")

            except PermissionError:
                return f"Error: Permission denied removing '{dir_name}'"
            except OSError as e:
                return f"Error removing '{dir_name}': {str(e)}"

        return f"Removed: {', '.join(removed_dirs)}"

    except Exception as e:
        return f"Error removing directories: {str(e)}"


def touch_command(cwd: str, args: List[str]) -> str:
    """
    Create empty file (Linux/macOS style).

    Args:
        cwd (str): Current working directory
        args (List[str]): Command arguments

    Returns:
        str: Success or error message
    """
    if not args:
        return "Error: touch requires a file name"

    try:
        created_files = []

        for file_name in args:
            file_path = normalize_path(file_name, cwd)

            if not is_safe_path(file_path, cwd):
                return f"Error: Access denied - path outside allowed directories"

            try:
                # Create empty file
                with open(file_path, 'a'):
                    pass

                # Update timestamp if file already exists
                os.utime(file_path, None)
                created_files.append(f"file '{file_name}'")

            except PermissionError:
                return f"Error: Permission denied creating '{file_name}'"
            except OSError as e:
                return f"Error creating '{file_name}': {str(e)}"

        return f"Created: {', '.join(created_files)}"

    except Exception as e:
        return f"Error creating files: {str(e)}"


def copy_command(cwd: str, args: List[str]) -> str:
    """
    Copy file (Windows style).

    Args:
        cwd (str): Current working directory
        args (List[str]): Command arguments

    Returns:
        str: Success or error message
    """
    if len(args) < 2:
        return "Error: copy requires source and destination"

    try:
        source = args[0]
        destination = args[1]

        source_path = normalize_path(source, cwd)
        dest_path = normalize_path(destination, cwd)

        if not is_safe_path(source_path, cwd) or not is_safe_path(dest_path, cwd):
            return f"Error: Access denied - path outside allowed directories"

        if not os.path.exists(source_path):
            return f"Error: Source '{source}' not found"

        try:
            if os.path.isdir(source_path):
                # Copy directory
                shutil.copytree(source_path, dest_path)
                return f"Copied directory '{source}' to '{destination}'"
            else:
                # Copy file
                shutil.copy2(source_path, dest_path)
                return f"Copied file '{source}' to '{destination}'"

        except PermissionError:
            return f"Error: Permission denied copying '{source}'"
        except OSError as e:
            return f"Error copying '{source}': {str(e)}"

    except Exception as e:
        return f"Error copying files: {str(e)}"


def move_command(cwd: str, args: List[str]) -> str:
    """
    Move/rename file or directory (Windows style).

    Args:
        cwd (str): Current working directory
        args (List[str]): Command arguments

    Returns:
        str: Success or error message
    """
    if len(args) < 2:
        return "Error: move requires source and destination"

    try:
        source = args[0]
        destination = args[1]

        source_path = normalize_path(source, cwd)
        dest_path = normalize_path(destination, cwd)

        if not is_safe_path(source_path, cwd) or not is_safe_path(dest_path, cwd):
            return f"Error: Access denied - path outside allowed directories"

        if not os.path.exists(source_path):
            return f"Error: Source '{source}' not found"

        try:
            shutil.move(source_path, dest_path)
            return f"Moved '{source}' to '{destination}'"

        except PermissionError:
            return f"Error: Permission denied moving '{source}'"
        except OSError as e:
            return f"Error moving '{source}': {str(e)}"

    except Exception as e:
        return f"Error moving files: {str(e)}"


def cp_command(cwd: str, args: List[str]) -> str:
    """
    Copy file or directory (Linux/macOS style).

    Args:
        cwd (str): Current working directory
        args (List[str]): Command arguments

    Returns:
        str: Success or error message
    """
    return copy_command(cwd, args)


def mv_command(cwd: str, args: List[str]) -> str:
    """
    Move/rename file or directory (Linux/macOS style).

    Args:
        cwd (str): Current working directory
        args (List[str]): Command arguments

    Returns:
        str: Success or error message
    """
    return move_command(cwd, args)


def del_command(cwd: str, args: List[str]) -> str:
    """
    Delete file (Windows style).

    Args:
        cwd (str): Current working directory
        args (List[str]): Command arguments

    Returns:
        str: Success or error message
    """
    if not args:
        return "Error: del requires a file name"

    try:
        deleted_files = []

        for file_name in args:
            file_path = normalize_path(file_name, cwd)

            if not is_safe_path(file_path, cwd):
                return f"Error: Access denied - path outside allowed directories"

            if not os.path.exists(file_path):
                return f"Error: File '{file_name}' not found"

            # Enhanced safety check for Ubuntu system protection
            is_safe, reason = is_safe_to_delete(file_path)
            if not is_safe:
                return f"Error: Cannot delete '{file_name}' - {reason}"

            if os.path.isdir(file_path):
                return f"Error: '{file_name}' is a directory (use rmdir for directories)"

            try:
                os.remove(file_path)
                deleted_files.append(f"file '{file_name}'")

            except PermissionError:
                return f"Error: Permission denied deleting '{file_name}'"
            except OSError as e:
                return f"Error deleting '{file_name}': {str(e)}"

        return f"Deleted: {', '.join(deleted_files)}"

    except Exception as e:
        return f"Error deleting files: {str(e)}"


def dir_command(cwd: str, args: List[str]) -> str:
    """
    List directory contents (Windows style).

    Args:
        cwd (str): Current working directory
        args (List[str]): Command arguments

    Returns:
        str: Formatted directory listing
    """
    # Use the same logic as ls_command but with Windows-style formatting
    return ls_command(cwd, args)
