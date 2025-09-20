"""
Terminal backend with command execution and routing.
"""
import os
from typing import Tuple, Optional
from commands.file_ops import (
    ls_command, cd_command, pwd_command, mkdir_command, rm_command,
    rmdir_command, touch_command, copy_command, move_command,
    cp_command, mv_command, del_command, dir_command
)
from commands.system_ops import cpu_command, mem_command, ps_command, disk_command
from nlp.interpreter import interpret_nl_query, is_nlp_command, extract_nlp_query


class CommandExecutor:
    """Handles command parsing, routing, and execution."""

    def __init__(self):
        """Initialize the command executor with command mappings."""
        self.commands = {
            # Navigation commands
            "ls": ls_command,
            "dir": dir_command,
            "cd": cd_command,
            "pwd": pwd_command,
            "root": self._root_command,

            # Directory operations
            "mkdir": mkdir_command,
            "rmdir": rmdir_command,

            # File operations
            "rm": rm_command,
            "del": del_command,
            "touch": touch_command,
            "copy": copy_command,
            "cp": cp_command,
            "move": move_command,
            "mv": mv_command,

            # System monitoring
            "cpu": cpu_command,
            "mem": mem_command,
            "ps": ps_command,
            "disk": disk_command,

            # Special commands
            "help": self._help_command,
            "clear": self._clear_command,
            "exit": self._exit_command,
            "quit": self._exit_command,
        }

    def execute_command(self, command: str, cwd: str) -> Tuple[str, str, bool]:
        """
        Execute a command and return output, new cwd, and whether to continue.

        Args:
            command (str): The command to execute
            cwd (str): Current working directory

        Returns:
            Tuple[str, str, bool]: (output, new_cwd, should_continue)
        """
        try:
            # Handle empty command
            if not command.strip():
                return "", cwd, True

            # Handle NLP commands
            if is_nlp_command(command):
                nl_query = extract_nl_query(command)
                translated_command = interpret_nl_query(nl_query)
                return self.execute_command(translated_command, cwd)

            # Parse command and arguments
            parts = command.strip().split()
            if not parts:
                return "", cwd, True

            cmd = parts[0].lower()
            args = parts[1:] if len(parts) > 1 else []

            # Check if command exists
            if cmd not in self.commands:
                return f"Command not found: {cmd}\nType 'help' for available commands", cwd, True

            # Execute the command
            handler = self.commands[cmd]

            # Commands that change directory return (output, new_cwd)
            if cmd in ["cd", "root"]:
                if cmd == "root":
                    output, new_cwd = handler(args)
                else:
                    output, new_cwd = handler(cwd, args)
                return output, new_cwd, True

            # Commands that don't change directory
            elif cmd in ["ls", "dir", "pwd", "mkdir", "rmdir", "rm", "del", "touch", "copy", "cp", "move", "mv"]:
                output = handler(cwd, args)
                return output, cwd, True

            # System monitoring commands
            elif cmd in ["cpu", "mem", "ps", "disk"]:
                output = handler(args)
                return output, cwd, True

            # Special commands
            elif cmd in ["help", "clear", "exit", "quit"]:
                output = handler(args)
                should_continue = cmd not in ["exit", "quit"]
                return output, cwd, should_continue

            else:
                return f"Command not found: {cmd}", cwd, True

        except Exception as e:
            return f"Error executing command: {str(e)}", cwd, True

    def _root_command(self, args: list) -> Tuple[str, str]:
        """Change to root directory."""
        import os
        root_dir = os.path.abspath(os.sep)
        return "", root_dir

    def _help_command(self, args: list) -> str:
        """Display help information."""
        help_text = """
=== Available Commands ===

Navigation Commands:
  ls [options] [directory]  - List directory contents (Linux/macOS)
                            - Options: -l (long format), -a (show hidden)
  dir [options] [directory] - List directory contents (Windows)
  cd [directory]           - Change directory
  pwd                      - Print working directory
  root                     - Change to root directory

Directory Operations:
  mkdir <name>             - Create directory
  rmdir <name>             - Remove empty directory (Windows style)

File Operations:
  rm [options] <name>      - Remove file or directory (Linux/macOS)
                            - Options: -r (recursive for directories)
  del <file>               - Delete file (Windows style)
  touch <file>             - Create empty file (Linux/macOS)
  copy <src> <dest>        - Copy file/directory (Windows style)
  cp <src> <dest>          - Copy file/directory (Linux/macOS style)
  move <src> <dest>        - Move/rename file/directory (Windows style)
  mv <src> <dest>          - Move/rename file/directory (Linux/macOS style)

System Monitoring:
  cpu                      - Show CPU usage information
  mem                      - Show memory usage information
  ps [options]             - Show running processes
                            - Options: -a (show all), <number> (limit results)
  disk                     - Show disk usage information

Special Commands:
  help                     - Show this help message
  clear                    - Clear the terminal
  exit/quit                - Exit the terminal

NLP Commands:
  !nlp <query>             - Natural language command (experimental)
                            - Example: !nlp show me the files
                            - Example: !nlp create a new file called test.txt
                            - Example: !nlp copy file1 to file2

Cross-Platform Support:
  - All commands work on Windows, macOS, and Linux
  - Use Windows-style commands (dir, copy, move, del) or Linux-style (ls, cp, mv, rm)
  - Path separators work with both / and \\

Note: File operations are now more permissive for better usability.
        """
        return help_text.strip()

    def _clear_command(self, args: list) -> str:
        """Clear command - returns special marker for UI to handle."""
        return "CLEAR_TERMINAL"

    def _exit_command(self, args: list) -> str:
        """Exit command."""
        return "Exiting terminal... Goodbye!"

    def get_available_commands(self) -> list:
        """Get list of available commands."""
        return list(self.commands.keys())

    def is_valid_command(self, command: str) -> bool:
        """Check if a command is valid."""
        parts = command.strip().split()
        if not parts:
            return False

        cmd = parts[0].lower()
        return cmd in self.commands or is_nlp_command(command)
