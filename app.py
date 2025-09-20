"""
Main Streamlit application for the custom terminal with keyboard history navigation.
"""
import streamlit as st
import os
from pathlib import Path
from terminal_backend import CommandExecutor
from utils.history import CommandHistory
from utils.helpers import get_home_directory


def initialize_session_state():
    """Initialize Streamlit session state variables."""
    if 'cwd' not in st.session_state:
        st.session_state.cwd = get_home_directory()

    if 'command_history' not in st.session_state:
        st.session_state.command_history = CommandHistory()

    if 'terminal_output' not in st.session_state:
        st.session_state.terminal_output = []

    if 'current_input' not in st.session_state:
        st.session_state.current_input = ""

    if 'history_index' not in st.session_state:
        st.session_state.history_index = -1

    if 'show_welcome' not in st.session_state:
        st.session_state.show_welcome = True

    if 'arrow_key' not in st.session_state:
        st.session_state.arrow_key = ""

    # Store the original app directory to prevent Streamlit issues
    if 'app_directory' not in st.session_state:
        st.session_state.app_directory = os.getcwd()


def get_prompt(cwd: str) -> str:
    """Generate the terminal prompt."""
    display_path = os.path.basename(
        cwd) if cwd != os.path.expanduser("~") else "~"
    return f"user@python-terminal:{display_path}$"


def add_to_output(text: str):
    """Add text to terminal output."""
    if text and text != "CLEAR_TERMINAL":
        st.session_state.terminal_output.append(text)


def clear_terminal():
    """Clear terminal output."""
    st.session_state.terminal_output = []
    st.session_state.show_welcome = False


def handle_command(command: str):
    """Handle command execution."""
    if not command.strip():
        return

    # Add command to history
    st.session_state.command_history.add_command(command)
    st.session_state.history_index = -1  # Reset history navigation

    # Add command to output
    add_to_output(f"{get_prompt(st.session_state.cwd)} {command}")

    # Execute command
    executor = CommandExecutor()
    output, new_cwd, should_continue = executor.execute_command(
        command, st.session_state.cwd)

    # Update working directory if changed (tracked in session state only)
    # Note: We don't change the actual OS working directory to avoid breaking Streamlit
    if new_cwd != st.session_state.cwd:
        st.session_state.cwd = new_cwd

    # Add output to terminal
    if output:
        if output == "CLEAR_TERMINAL":
            clear_terminal()
        else:
            add_to_output(output)

    # Check if should exit
    if not should_continue:
        st.session_state.terminal_output.append("Terminal session ended.")
        st.stop()


def handle_history_navigation(direction: str):
    """Handle history navigation (up/down arrows)."""
    if direction == "up":
        prev_cmd = st.session_state.command_history.get_previous()
        if prev_cmd is not None:
            st.session_state.current_input = prev_cmd
    elif direction == "down":
        next_cmd = st.session_state.command_history.get_next()
        if next_cmd is not None:
            st.session_state.current_input = next_cmd
        else:
            st.session_state.current_input = ""


def main():
    """Main application function."""
    st.set_page_config(
        page_title="Python Terminal",
        page_icon="💻",
        layout="wide",
        initial_sidebar_state="collapsed"
    )

    initialize_session_state()

    # Custom CSS
    st.markdown("""
    <style>
    .terminal-body { overflow-y:auto; height:70vh; }
    .terminal-output { color: #00ff00; white-space: pre-wrap; }
    .terminal-prompt { color:#00ff00; margin-right:5px; }
    .terminal-input-line { display:flex; align-items:center; margin-top:5px; }
    .stTextInput>div>div>input { background:transparent !important; color:#00ff00 !important; border:none !important; }
    .stTextInput>div>div>input::placeholder { color:#666 !important; }
    </style>
    """, unsafe_allow_html=True)

    # Terminal header
    st.markdown("""
    <div style="background-color:#2d2d2d; padding:8px; color:#fff; border-radius:6px 6px 0 0;">
        🐍 Python Terminal
    </div>
    """, unsafe_allow_html=True)

    # Terminal body
    st.markdown('<div class="terminal-body">', unsafe_allow_html=True)

    # Welcome message
    if st.session_state.show_welcome and not st.session_state.terminal_output:
        st.markdown("""
        <div style="color:#00ff00;">
        Welcome to Python Terminal!<br>
        Type 'help' for available commands or '!nlp' for natural language commands.<br><br>
        </div>
        """, unsafe_allow_html=True)

    # Terminal output
    for output in st.session_state.terminal_output:
        st.markdown(
            f'<div class="terminal-output">{output}</div>', unsafe_allow_html=True)

    # Current working directory
    st.markdown(
        f'<div class="terminal-prompt">Current Directory: {st.session_state.cwd}</div>', unsafe_allow_html=True)

    # Input form
    with st.form("terminal_form", clear_on_submit=True):
        st.markdown('<div class="terminal-input-line">',
                    unsafe_allow_html=True)
        st.markdown(
            f'<span class="terminal-prompt">{get_prompt(st.session_state.cwd)}</span>', unsafe_allow_html=True)

        command_input = st.text_input(
            "Command Input",
            value=st.session_state.current_input,
            placeholder="Enter command...",
            key="command_input",
            label_visibility="collapsed"
        )

        # Hidden field for arrow keys
        st.text_input("arrow_key", value="", key="arrow_key",
                      label_visibility="collapsed")

        st.markdown('</div>', unsafe_allow_html=True)

        col1, col2, col3, col4 = st.columns(4)
        with col1:
            submit_button = st.form_submit_button("Execute")
        with col2:
            clear_button = st.form_submit_button("Clear")
        with col3:
            help_button = st.form_submit_button("Help")
        with col4:
            pwd_button = st.form_submit_button("PWD")

    # Inject JS for arrow key detection
    st.markdown("""
    <script>
    const input = window.parent.document.querySelector('input[id*="command_input"]');
    const arrow_input = window.parent.document.querySelector('input[id*="arrow_key"]');
    if(input && arrow_input){
        input.addEventListener('keydown', (e) => {
            if(e.key === 'ArrowUp'){
                arrow_input.value = 'up';
                arrow_input.dispatchEvent(new Event('input'));
                e.preventDefault();
            } else if(e.key === 'ArrowDown'){
                arrow_input.value = 'down';
                arrow_input.dispatchEvent(new Event('input'));
                e.preventDefault();
            }
        });
    }
    </script>
    """, unsafe_allow_html=True)

    # Handle arrow keys
    if st.session_state.arrow_key == "up":
        handle_history_navigation("up")
        st.session_state.arrow_key = ""
        st.rerun()

    if st.session_state.arrow_key == "down":
        handle_history_navigation("down")
        st.session_state.arrow_key = ""
        st.rerun()

    # Quick command buttons
    quick_commands = ["ls -la", "touch test.txt",
                      "mkdir test_dir", "copy", "move", "help"]
    cols = st.columns(len(quick_commands))
    for i, cmd in enumerate(quick_commands):
        with cols[i]:
            if st.button(cmd, key=f"quick_cmd_{i}_{cmd.replace(' ', '_')}"):
                handle_command(cmd)
                st.rerun()

    st.markdown('</div>', unsafe_allow_html=True)  # close terminal-body

    # Status bar
    st.markdown(f"""
    <div style="background-color:#2d2d2d; padding:5px; color:#ccc; border-radius:0 0 6px 6px;">
        Ready | Commands: {len(st.session_state.command_history.get_history())} | Python Terminal v1.0
    </div>
    """, unsafe_allow_html=True)

    # Handle form submissions
    if submit_button and command_input:
        handle_command(command_input)
        st.session_state.current_input = ""
        st.rerun()

    if clear_button:
        clear_terminal()
        st.session_state.current_input = ""
        st.rerun()

    if help_button:
        handle_command("help")
        st.session_state.current_input = ""
        st.rerun()

    if pwd_button:
        handle_command("pwd")
        st.session_state.current_input = ""
        st.rerun()


if __name__ == "__main__":
    main()
