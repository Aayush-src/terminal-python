"""
Command history management for terminal navigation.
"""
from typing import List, Optional


class CommandHistory:
    """Manages command history with navigation support."""

    def __init__(self):
        self.history: List[str] = []
        self.current_index: int = -1

    def add_command(self, command: str) -> None:
        """
        Add a command to history.

        Args:
            command (str): The command to add
        """
        if command.strip() and (not self.history or self.history[-1] != command.strip()):
            self.history.append(command.strip())
            self.current_index = len(self.history)

    def get_previous(self) -> Optional[str]:
        """
        Get the previous command in history (UP arrow).

        Returns:
            Optional[str]: Previous command or None if at beginning
        """
        if self.current_index > 0:
            self.current_index -= 1
            return self.history[self.current_index]
        return None

    def get_next(self) -> Optional[str]:
        """
        Get the next command in history (DOWN arrow).

        Returns:
            Optional[str]: Next command or None if at end
        """
        if self.current_index < len(self.history) - 1:
            self.current_index += 1
            return self.history[self.current_index]
        elif self.current_index == len(self.history) - 1:
            self.current_index = len(self.history)
            return ""
        return None

    def reset_navigation(self) -> None:
        """Reset navigation to the end of history."""
        self.current_index = len(self.history)

    def get_history(self) -> List[str]:
        """
        Get the complete command history.

        Returns:
            List[str]: List of all commands in history
        """
        return self.history.copy()

    def clear_history(self) -> None:
        """Clear all command history."""
        self.history.clear()
        self.current_index = -1

    def get_current_command(self) -> Optional[str]:
        """
        Get the current command at the navigation index.

        Returns:
            Optional[str]: Current command or None
        """
        if 0 <= self.current_index < len(self.history):
            return self.history[self.current_index]
        return None
