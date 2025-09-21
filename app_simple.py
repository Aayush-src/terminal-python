"""
Simple Streamlit terminal with one input field and two navigation buttons.
"""
import streamlit as st
import os
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

    if 'show_welcome' not in st.session_state:
        st.session_state.show_welcome = True


def get_prompt(cwd: str) -> str:
    """Generate the terminal prompt."""
    # Always show the actual current directory path
    display_path = cwd
    return f"{display_path}$"


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

    # Add command to output
    add_to_output(f"{get_prompt(st.session_state.cwd)} {command}")

    # Enhanced NLP processing
    if is_nlp_command(command):
        nlp_query = extract_nlp_query(command)
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

    # Update working directory if changed
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
    """Handle history navigation."""
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
        page_title="AI based Terminal",
        page_icon="",
        layout="wide",
        initial_sidebar_state="collapsed"
    )

    # Initialize session state
    initialize_session_state()

    # Simple Terminal CSS
    st.markdown("""
    <style>
    /* Hide Streamlit elements */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
    
    /* Terminal styling */
    .stApp {
        background: #000000;
        color: #ffffff;
    }
    
     .main .block-container {
         padding: 20px;
         max-width: 100%;
    }
    
    /* Terminal output area */
    .terminal-output {
        background: #000000;
        color: #ffffff;
        border: 1px solid #333;
        border-radius: 5px;
        padding: 15px;
        font-family: 'Consolas', 'Monaco', 'Courier New', monospace;
        font-size: 14px;
        line-height: 1.4;
        min-height: 400px;
        max-height: 500px;
        overflow-y: auto;
        white-space: pre-wrap;
        margin-bottom: 20px;
    }
    
    .terminal-output .prompt {
        color: #00ff00;
        font-weight: bold;
    }
    
    .terminal-output .command {
        color: #00ff00;
    }
    
    .terminal-output .error {
        color: #ff6b6b;
    }
    
    .terminal-output .success {
        color: #51cf66;
    }
    
    /* Input area */
    .input-area {
        display: flex;
        align-items: center;
        gap: 0px;
        margin-bottom: 10px;
    }
    
    .terminal-prompt {
        color: #00ff00;
        font-weight: bold;
        font-family: 'Consolas', 'Monaco', 'Courier New', monospace;
        font-size: 14px;
        white-space: nowrap;
        margin-right: 0px;
    }
    
    /* Input field styling */
    .stTextInput > div > div > input {
        background: #000000 !important;
        color: #00ff00 !important;
        border: 1px solid #333 !important;
        font-family: 'Consolas', 'Monaco', 'Courier New', monospace !important;
        font-size: 14px !important;
        padding: 8px !important;
        border-radius: 3px !important;
        caret-color: #00ff00 !important;
        margin-left: 0px !important;
    }
    
    .stTextInput > div > div > input:focus {
        border-color: #00ff00 !important;
        box-shadow: 0 0 5px rgba(0, 255, 0, 0.3) !important;
    }
    
    /* Button styling */
    .stButton > button {
        background: #2d2d2d !important;
        color: #00ff00 !important;
        border: 1px solid #444 !important;
        font-family: 'Consolas', 'Monaco', 'Courier New', monospace !important;
        font-size: 12px !important;
        padding: 6px 12px !important;
        border-radius: 3px !important;
        transition: all 0.2s !important;
    }
    
    .stButton > button:hover {
        background: #3d3d3d !important;
        border-color: #00ff00 !important;
    }
    
    /* Welcome message */
    .welcome-message {
        color: #ffffff;
        font-family: 'Consolas', 'Monaco', 'Courier New', monospace;
        line-height: 1.4;
        margin-bottom: 20px;
    }
    
    .welcome-message .title {
        color: #ffffff;
        font-weight: bold;
    }
    </style>
    """, unsafe_allow_html=True)

    # Title
    st.title(" Python Terminal")

    # Welcome message
    if st.session_state.show_welcome and not st.session_state.terminal_output:
        st.markdown("""
        <div class="welcome-message">
        <span class="title">🚀 Simple Python Terminal with NLP</span><br><br>
        • Type commands and press Enter to execute<br>
        • Use ↑/↓ buttons to navigate command history<br>
        • Try 'help' for available commands<br>
        • Try '!nlp show me the files' for NLP features<br>
        </div>
        """, unsafe_allow_html=True)

    # Terminal output area
   # st.markdown('<div class="terminal-output">', unsafe_allow_html=True)

    # Display terminal output
    for output in st.session_state.terminal_output:
        if "Error:" in output or "error" in output.lower():
            st.markdown(
                f'<div class="error">{output}</div>', unsafe_allow_html=True)
        elif "Success:" in output or "✓" in output:
            st.markdown(
                f'<div class="success">{output}</div>', unsafe_allow_html=True)
        elif output.startswith("user@"):
            # Extract the current directory from the prompt and show it properly
            prompt_part = output.split("$")[0] + "$"
            command_part = output.split("$")[1] if "$" in output else ""
            st.markdown(
                f'<div><span class="prompt">{prompt_part}</span><span class="command">{command_part}</span></div>', unsafe_allow_html=True)
        else:
            st.markdown(f'<div>{output}</div>', unsafe_allow_html=True)

    st.markdown('</div>', unsafe_allow_html=True)

    # Input area with prompt and text input
    col1, col2 = st.columns([1, 4])

    with col1:
        st.markdown(f'<div class="terminal-prompt">{get_prompt(st.session_state.cwd)}</div>',
                    unsafe_allow_html=True)

    with col2:
        command_input = st.text_input(
            "Command Input",
            value=st.session_state.current_input,
            placeholder="Type command here...",
            key="command_input",
            label_visibility="collapsed"
        )

    # Navigation buttons
    col1, col2, col3 = st.columns([1, 1, 1])

    with col1:
        if st.button("Previous Command", key="prev_btn"):
            handle_history_navigation("up")
            st.rerun()

    with col2:
        if st.button(" Forward Comamnd", key="next_btn"):
            handle_history_navigation("down")
            st.rerun()

    with col3:
        if st.button("Clear", key="clear_btn"):
            clear_terminal()
            st.session_state.current_input = ""
            st.rerun()

    # Handle Enter key press
    if command_input:
        # Check if this is a new command (not from history navigation)
        if command_input != st.session_state.get('last_command', ''):
            handle_command(command_input)
            st.session_state.current_input = ""
            st.session_state.last_command = command_input
            st.rerun()

    # JavaScript for Enter key handling
    st.markdown("""
    <script>
    document.addEventListener('DOMContentLoaded', function() {
        const input = document.querySelector('input[aria-label="Command Input"]');
        if (input) {
            input.focus();
            
            input.addEventListener('keydown', function(e) {
                if (e.key === 'Enter') {
                    // The form will handle the submission
                    return true;
                }
            });
        }
    });
    </script>
    """, unsafe_allow_html=True)


if __name__ == "__main__":
    main()
