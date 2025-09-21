"""
Terminal backend with command execution and routing.
"""
import os
import sys
import subprocess
import importlib.util
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

            # Handle multi-step commands (separated by &&)
            if ' && ' in command:
                return self.execute_multi_step_command(command, cwd)

            # Handle NLP commands
            if is_nlp_command(command):
                nl_query = extract_nlp_query(command)
                translated_command = interpret_nl_query(nl_query)
                return self.execute_command(translated_command, cwd)

            # Parse command and arguments
            parts = command.strip().split()
            if not parts:
                return "", cwd, True

            cmd = parts[0].lower()
            args = parts[1:] if len(parts) > 1 else []

            # Check if command exists or is pip command
            if cmd not in self.commands and cmd != "pip":
                return f"Command not found: {cmd}\nType 'help' for available commands", cwd, True

            # Handle pip commands
            if cmd == "pip":
                output = self.handle_pip_command(parts)
                return output, cwd, True

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

    def execute_multi_step_command(self, command: str, cwd: str) -> Tuple[str, str, bool]:
        """
        Execute multiple commands separated by &&.

        Args:
            command (str): Multi-step command (e.g., "mkdir test && move file.txt test")
            cwd (str): Current working directory

        Returns:
            Tuple[str, str, bool]: (combined_output, final_cwd, should_continue)
        """
        try:
            steps = command.split(' && ')
            outputs = []
            current_cwd = cwd

            for step in steps:
                step = step.strip()
                if not step:
                    continue

                output, new_cwd, should_continue = self.execute_command(
                    step, current_cwd)
                outputs.append(output)
                current_cwd = new_cwd

                if not should_continue:
                    break

            # Combine outputs
            combined_output = '\n'.join(filter(None, outputs))
            return combined_output, current_cwd, True

        except Exception as e:
            return f"Error executing multi-step command: {str(e)}", cwd, True

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

Package Management:
  pip install <package>    - Install a Python package
  pip uninstall <package>  - Uninstall a Python package
  pip list                 - List all installed packages
  pip check <package>      - Check if a package is installed
  
  Note: In hosted environments (like Streamlit Cloud), some packages
        may fail to install due to permission restrictions.

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
  - Pip commands use the current Python environment

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
        return cmd in self.commands or is_nlp_command(command) or cmd == "pip"

    def handle_pip_command(self, cmd_tokens: list[str], simulate: bool = False) -> str:
        """
        Handle pip package management commands.

        Args:
            cmd_tokens: List of command tokens (e.g., ['pip', 'install', 'numpy'])
            simulate: If True, simulate the operation without actually executing

        Returns:
            str: Output message for the terminal
        """
        if len(cmd_tokens) < 2:
            return "Usage: pip <install|uninstall|list|check> [package_name]"

        operation = cmd_tokens[1].lower()
        package_name = cmd_tokens[2] if len(cmd_tokens) > 2 else None

        try:
            if operation == "install":
                if not package_name:
                    return "Error: Package name required for install command"
                return self._pip_install(package_name, simulate)

            elif operation == "uninstall":
                if not package_name:
                    return "Error: Package name required for uninstall command"
                return self._pip_uninstall(package_name, simulate)

            elif operation == "list":
                return self._pip_list(simulate)

            elif operation == "check":
                if not package_name:
                    return "Error: Package name required for check command"
                return self._pip_check(package_name, simulate)

            else:
                return f"Error: Unknown pip operation '{operation}'. Available: install, uninstall, list, check"

        except Exception as e:
            return f"Error executing pip command: {str(e)}"

    def _pip_install(self, package_name: str, simulate: bool = False) -> str:
        """Install a package using pip."""
        if simulate:
            return f"🔧 [SIMULATE] Installing {package_name}...\n✅ [SIMULATE] {package_name} installed successfully."

        try:
            # Check if already installed
            if self._is_package_installed(package_name):
                return f"ℹ️  {package_name} is already installed."

            print(f"Installing {package_name}...")

            # Use sys.executable to ensure correct Python environment
            result = subprocess.run(
                [sys.executable, "-m", "pip", "install", package_name, "--user"],
                capture_output=True,
                text=True,
                check=True
            )

            return f"✅ {package_name} installed successfully."

        except subprocess.CalledProcessError as e:
            error_msg = e.stderr.strip() if e.stderr else "Unknown error occurred"

            # Handle common permission errors
            if "Permission denied" in error_msg or "Errno 13" in error_msg:
                return f"❌ Permission denied: Cannot install {package_name} on this server.\n💡 This is a hosted environment with restricted permissions.\n🔧 Try: pip install {package_name} --user (if supported)"
            elif "Could not install packages" in error_msg:
                return f"❌ Installation failed: {package_name} cannot be installed on this server.\n💡 Some packages require system-level access that's not available in hosted environments."
            else:
                return f"❌ Failed to install {package_name}: {error_msg}"
        except Exception as e:
            return f"❌ Error installing {package_name}: {str(e)}"

    def _pip_uninstall(self, package_name: str, simulate: bool = False) -> str:
        """Uninstall a package using pip."""
        if simulate:
            return f"🔧 [SIMULATE] Uninstalling {package_name}...\n✅ [SIMULATE] {package_name} removed successfully."

        try:
            # Check if package is installed
            if not self._is_package_installed(package_name):
                return f"ℹ️  {package_name} is not installed."

            print(f"Uninstalling {package_name}...")

            # Use sys.executable to ensure correct Python environment
            result = subprocess.run(
                [sys.executable, "-m", "pip", "uninstall", package_name, "-y"],
                capture_output=True,
                text=True,
                check=True
            )

            return f"✅ {package_name} removed successfully."

        except subprocess.CalledProcessError as e:
            error_msg = e.stderr.strip() if e.stderr else "Unknown error occurred"

            # Handle common permission errors
            if "Permission denied" in error_msg or "Errno 13" in error_msg:
                return f"❌ Permission denied: Cannot uninstall {package_name} on this server.\n💡 This is a hosted environment with restricted permissions."
            else:
                return f"❌ Failed to uninstall {package_name}: {error_msg}"
        except Exception as e:
            return f"❌ Error uninstalling {package_name}: {str(e)}"

    def _pip_list(self, simulate: bool = False) -> str:
        """List installed packages."""
        if simulate:
            return "🔧 [SIMULATE] Listing installed packages...\n📦 [SIMULATE] numpy==1.21.0\n📦 [SIMULATE] pandas==1.3.0\n📦 [SIMULATE] requests==2.25.1"

        try:
            # Use sys.executable to ensure correct Python environment
            result = subprocess.run(
                [sys.executable, "-m", "pip", "list"],
                capture_output=True,
                text=True,
                check=True
            )

            # Clean up the output for better display
            output_lines = result.stdout.strip().split('\n')
            if len(output_lines) > 2:  # Skip header lines
                # Skip "Package Version" and "---" lines
                packages = output_lines[2:]
                formatted_packages = []
                for package in packages:
                    if package.strip():
                        formatted_packages.append(f"📦 {package.strip()}")

                if formatted_packages:
                    return "Installed packages:\n" + "\n".join(formatted_packages)
                else:
                    return "No packages found."
            else:
                return "No packages found."

        except subprocess.CalledProcessError as e:
            error_msg = e.stderr.strip() if e.stderr else "Unknown error occurred"
            return f"❌ Failed to list packages: {error_msg}"
        except Exception as e:
            return f"❌ Error listing packages: {str(e)}"

    def _pip_check(self, package_name: str, simulate: bool = False) -> str:
        """Check if a package is installed."""
        if simulate:
            return f"🔧 [SIMULATE] Checking if {package_name} is installed...\n✅ [SIMULATE] {package_name} is installed."

        try:
            if self._is_package_installed(package_name):
                return f"✅ {package_name} is installed."
            else:
                return f"❌ {package_name} is not installed."

        except Exception as e:
            return f"❌ Error checking {package_name}: {str(e)}"

    def _is_package_installed(self, package_name: str) -> bool:
        """Check if a package is installed using importlib.util.find_spec."""
        try:
            spec = importlib.util.find_spec(package_name)
            return spec is not None
        except (ImportError, ValueError, AttributeError):
            return False
