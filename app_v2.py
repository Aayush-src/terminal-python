"""
Enhanced Streamlit terminal application with form structure and advanced NLP.
"""
import streamlit as st
import os
import json
from pathlib import Path
from terminal_backend import CommandExecutor
from utils.history import CommandHistory
from utils.helpers import get_home_directory
from nlp.interpreter import interpret_nl_query, is_nlp_command, extract_nlp_query


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

    if 'app_directory' not in st.session_state:
        st.session_state.app_directory = os.getcwd()

    if 'command_buffer' not in st.session_state:
        st.session_state.command_buffer = ""

    if 'nlp_context' not in st.session_state:
        st.session_state.nlp_context = {
            'last_commands': [],
            'user_preferences': {},
            'conversation_history': []
        }


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
    """Handle command execution with enhanced NLP support."""
    if not command.strip():
        return

    # Add command to history
    st.session_state.command_history.add_command(command)
    st.session_state.history_index = -1

    # Add command to output
    add_to_output(f"{get_prompt(st.session_state.cwd)} {command}")

    # Enhanced NLP processing
    if is_nlp_command(command):
        nlp_query = extract_nlp_query(command)
        st.session_state.nlp_context['conversation_history'].append({
            'type': 'user',
            'query': nlp_query,
            'timestamp': st.session_state.get('command_count', 0)
        })

        # Interpret NLP command
        interpreted_command = interpret_nl_query(nlp_query)
        add_to_output(f"NLP: {interpreted_command}")

        # Execute the interpreted command
        executor = CommandExecutor()
        output, new_cwd, should_continue = executor.execute_command(
            interpreted_command, st.session_state.cwd)
    else:
        # Regular command execution
        executor = CommandExecutor()
        output, new_cwd, should_continue = executor.execute_command(
            command, st.session_state.cwd)

    # Update working directory if changed (tracked in session state only)
    if new_cwd != st.session_state.cwd:
        st.session_state.cwd = new_cwd

    # Add output to terminal
    if output:
        if output == "CLEAR_TERMINAL":
            clear_terminal()
        else:
            add_to_output(output)

    # Update NLP context
    st.session_state.nlp_context['last_commands'].append(command)
    if len(st.session_state.nlp_context['last_commands']) > 10:
        st.session_state.nlp_context['last_commands'].pop(0)

    # Check if should exit
    if not should_continue:
        st.session_state.terminal_output.append("Terminal session ended.")
        st.stop()


def handle_history_navigation(direction: str):
    """Handle history navigation with enhanced context."""
    if direction == "up":
        prev_cmd = st.session_state.command_history.get_previous()
        if prev_cmd is not None:
            st.session_state.current_input = prev_cmd
            st.session_state.history_index = st.session_state.command_history.current_index
    elif direction == "down":
        next_cmd = st.session_state.command_history.get_next()
        if next_cmd is not None:
            st.session_state.current_input = next_cmd
            st.session_state.history_index = st.session_state.command_history.current_index
        else:
            st.session_state.current_input = ""


def get_suggestions(input_text: str) -> list:
    """Get command suggestions based on input and context."""
    suggestions = []
    input_lower = input_text.lower()

    # Basic command suggestions
    basic_commands = ['ls', 'cd', 'pwd', 'mkdir',
                      'touch', 'rm', 'cp', 'mv', 'help', 'clear']
    for cmd in basic_commands:
        if cmd.startswith(input_lower) and cmd != input_lower:
            suggestions.append(cmd)

    # Context-based suggestions
    if 'file' in input_lower:
        suggestions.extend(['touch', 'rm', 'cp', 'mv'])
    if 'dir' in input_lower or 'folder' in input_lower:
        suggestions.extend(['mkdir', 'ls', 'cd'])
    if 'show' in input_lower or 'list' in input_lower:
        suggestions.extend(['ls', 'ls -la', 'ps', 'cpu', 'mem'])

    return suggestions[:5]  # Limit to 5 suggestions


def main():
    """Main application function with enhanced UI."""
    st.set_page_config(
        page_title="Python Terminal",
        page_icon="🐍",
        layout="wide",
        initial_sidebar_state="collapsed"
    )

    # Initialize session state
    initialize_session_state()

    # Enhanced CSS for terminal-like appearance
    st.markdown("""
    <style>
    .terminal-container {
        background-color: #0c0c0c;
        color: #00ff00;
        font-family: 'Consolas', 'Monaco', 'Courier New', monospace;
        padding: 20px;
        border-radius: 10px;
        box-shadow: 0 4px 20px rgba(0, 0, 0, 0.5);
        min-height: 80vh;
    }
    
    .terminal-header {
        background-color: #2d2d2d;
        padding: 10px 15px;
        border-radius: 8px 8px 0 0;
        margin-bottom: 10px;
        display: flex;
        justify-content: space-between;
        align-items: center;
    }
    
    .terminal-title {
        color: #fff;
        font-size: 16px;
        font-weight: bold;
    }
    
    .terminal-status {
        color: #00ff00;
        font-size: 12px;
    }
    
    .terminal-body {
        background-color: #0c0c0c;
        padding: 15px;
        border-radius: 0 0 8px 8px;
        min-height: 60vh;
        max-height: 60vh;
        overflow-y: auto;
    }
    
    .terminal-output {
        color: #00ff00;
        white-space: pre-wrap;
        margin: 5px 0;
        line-height: 1.4;
    }
    
    .terminal-input-container {
        background-color: #1a1a1a;
        padding: 15px;
        border-radius: 8px;
        margin-top: 10px;
        border: 2px solid #333;
    }
    
    .terminal-prompt {
        color: #00ff00;
        font-weight: bold;
        margin-right: 10px;
    }
    
    .command-suggestions {
        background-color: #2d2d2d;
        padding: 10px;
        border-radius: 5px;
        margin-top: 10px;
        display: flex;
        flex-wrap: wrap;
        gap: 5px;
    }
    
    .suggestion-item {
        background-color: #444;
        color: #00ff00;
        padding: 5px 10px;
        border-radius: 3px;
        cursor: pointer;
        font-size: 12px;
    }
    
    .suggestion-item:hover {
        background-color: #555;
    }
    
    .nlp-indicator {
        background-color: #1e3a8a;
        color: #60a5fa;
        padding: 2px 6px;
        border-radius: 3px;
        font-size: 10px;
        margin-left: 5px;
    }
    
    .history-nav {
        display: flex;
        gap: 10px;
        margin: 10px 0;
    }
    
    .nav-button {
        background-color: #333;
        color: #00ff00;
        border: 1px solid #555;
        padding: 8px 15px;
        border-radius: 5px;
        cursor: pointer;
        font-family: 'Consolas', 'Monaco', 'Courier New', monospace;
        font-size: 12px;
    }
    
    .nav-button:hover {
        background-color: #444;
    }
    
    .quick-commands {
        display: flex;
        flex-wrap: wrap;
        gap: 5px;
        margin: 10px 0;
    }
    
    .quick-cmd {
        background-color: #1e40af;
        color: #dbeafe;
        padding: 5px 10px;
        border-radius: 3px;
        cursor: pointer;
        font-size: 11px;
        border: none;
    }
    
    .quick-cmd:hover {
        background-color: #1d4ed8;
    }
    
    .stTextInput > div > div > input {
        background-color: #1a1a1a !important;
        color: #00ff00 !important;
        border: 1px solid #555 !important;
        font-family: 'Consolas', 'Monaco', 'Courier New', monospace !important;
        font-size: 14px !important;
    }
    
    .stTextInput > div > div > input:focus {
        border-color: #00ff00 !important;
        box-shadow: 0 0 5px rgba(0, 255, 0, 0.3) !important;
    }
    
    .stButton > button {
        background-color: #333 !important;
        color: #00ff00 !important;
        border: 1px solid #555 !important;
        font-family: 'Consolas', 'Monaco', 'Courier New', monospace !important;
    }
    
    .stButton > button:hover {
        background-color: #444 !important;
    }
    </style>
    """, unsafe_allow_html=True)

    # Main terminal container
    st.markdown('<div class="terminal-container">', unsafe_allow_html=True)

    # Terminal header
    st.markdown(f"""
    <div class="terminal-header">
        <div class="terminal-title">🐍 Enhanced Python Terminal</div>
        <div class="terminal-status">
            Commands: {len(st.session_state.command_history.get_history())} | 
            CWD: {os.path.basename(st.session_state.cwd)} | 
            NLP: Ready
        </div>
    </div>
    """, unsafe_allow_html=True)

    # Terminal body
    st.markdown('<div class="terminal-body">', unsafe_allow_html=True)

    # Welcome message
    if st.session_state.show_welcome and not st.session_state.terminal_output:
        st.markdown("""
        <div class="terminal-output">
        🚀 Welcome to Enhanced Python Terminal!<br>
        <br>
        Features:<br>
        • Full file system navigation (ls, cd, mkdir, touch, cp, mv, rm)<br>
        • System monitoring (cpu, mem, ps, disk)<br>
        • Natural Language Processing (!nlp commands)<br>
        • Command history with UP/DOWN navigation<br>
        • Smart command suggestions<br>
        • Cross-platform compatibility<br>
        <br>
        Try: 'help' for commands, '!nlp show me the files' for NLP<br>
        </div>
        """, unsafe_allow_html=True)

    # Display terminal output
    for output in st.session_state.terminal_output:
        st.markdown(
            f'<div class="terminal-output">{output}</div>', unsafe_allow_html=True)

    st.markdown('</div>', unsafe_allow_html=True)  # Close terminal-body

    # Terminal input container
    st.markdown('<div class="terminal-input-container">',
                unsafe_allow_html=True)

    # Command input form
    with st.form("terminal_form", clear_on_submit=False):
        # Input field with prompt
        col1, col2 = st.columns([1, 20])

        with col1:
            st.markdown(f'<div class="terminal-prompt">{get_prompt(st.session_state.cwd)}</div>',
                        unsafe_allow_html=True)

        with col2:
            command_input = st.text_input(
                "Command Input",
                value=st.session_state.current_input,
                placeholder="Enter command or use !nlp for natural language...",
                key="command_input",
                label_visibility="collapsed"
            )

        # Form buttons
        col1, col2, col3, col4, col5 = st.columns(5)

        with col1:
            submit_button = st.form_submit_button("Execute", type="primary")

        with col2:
            clear_button = st.form_submit_button("Clear")

        with col3:
            help_button = st.form_submit_button("Help")

        with col4:
            history_button = st.form_submit_button("History")

        with col5:
            nlp_button = st.form_submit_button("NLP Help")

    # Command suggestions
    if command_input and len(command_input) > 0:
        suggestions = get_suggestions(command_input)
        if suggestions:
            st.markdown('<div class="command-suggestions">',
                        unsafe_allow_html=True)
            st.markdown('<span style="color: #ccc; font-size: 12px;">Suggestions: </span>',
                        unsafe_allow_html=True)
            for suggestion in suggestions:
                if st.button(suggestion, key=f"suggest_{suggestion}",
                             help=f"Use '{suggestion}'"):
                    st.session_state.current_input = suggestion
                    st.rerun()
            st.markdown('</div>', unsafe_allow_html=True)

    # History navigation
    st.markdown('<div class="history-nav">', unsafe_allow_html=True)
    st.markdown('<span style="color: #ccc; font-size: 12px;">History Navigation: </span>',
                unsafe_allow_html=True)

    col1, col2, col3, col4 = st.columns(4)

    with col1:
        if st.button("↑ Previous", key="hist_up_btn"):
            handle_history_navigation("up")
            st.rerun()

    with col2:
        if st.button("↓ Next", key="hist_down_btn"):
            handle_history_navigation("down")
            st.rerun()

    with col3:
        if st.button("🔄 Refresh", key="refresh_btn"):
            st.rerun()

    with col4:
        if st.button("📁 PWD", key="pwd_btn"):
            handle_command("pwd")
            st.rerun()

    st.markdown('</div>', unsafe_allow_html=True)

    # Quick commands
    st.markdown('<div class="quick-commands">', unsafe_allow_html=True)
    st.markdown('<span style="color: #ccc; font-size: 12px;">Quick Commands: </span>',
                unsafe_allow_html=True)

    quick_commands = [
        ("ls -la", "List files"),
        ("touch test.txt", "Create file"),
        ("mkdir test_dir", "Create directory"),
        ("cpu", "CPU usage"),
        ("mem", "Memory usage"),
        ("ps", "Processes"),
        ("!nlp help", "NLP help"),
        ("help", "All commands")
    ]

    for cmd, help_text in quick_commands:
        if st.button(cmd, key=f"quick_{cmd.replace(' ', '_')}",
                     help=help_text):
            handle_command(cmd)
            st.rerun()

    st.markdown('</div>', unsafe_allow_html=True)

    # JavaScript for keyboard navigation
    st.markdown("""
    <script>
    document.addEventListener('DOMContentLoaded', function() {
        const input = document.querySelector('input[aria-label="Command Input"]');
        if (input) {
            input.addEventListener('keydown', function(e) {
                if (e.key === 'ArrowUp') {
                    e.preventDefault();
                    // Trigger up navigation
                    const upBtn = document.querySelector('button[data-testid="baseButton-secondary"][aria-label="↑ Previous"]');
                    if (upBtn) upBtn.click();
                } else if (e.key === 'ArrowDown') {
                    e.preventDefault();
                    // Trigger down navigation
                    const downBtn = document.querySelector('button[data-testid="baseButton-secondary"][aria-label="↓ Next"]');
                    if (downBtn) downBtn.click();
                } else if (e.key === 'Tab') {
                    e.preventDefault();
                    // Auto-complete with first suggestion
                    const suggestions = document.querySelectorAll('.suggestion-item');
                    if (suggestions.length > 0) {
                        suggestions[0].click();
                    }
                }
            });
        }
    });
    </script>
    """, unsafe_allow_html=True)

    # Close terminal-input-container
    st.markdown('</div>', unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)  # Close terminal-container

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

    if history_button:
        history = st.session_state.command_history.get_history()
        if history:
            add_to_output("Command History:")
            for i, cmd in enumerate(history[-10:], 1):  # Show last 10 commands
                add_to_output(f"  {i}. {cmd}")
        else:
            add_to_output("No command history yet.")
        st.rerun()

    if nlp_button:
        handle_command("!nlp help")
        st.session_state.current_input = ""
        st.rerun()


if __name__ == "__main__":
    main()
