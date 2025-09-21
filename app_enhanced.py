"""
Enhanced Streamlit terminal application with advanced keyboard navigation and NLP.
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

    if 'keyboard_nav' not in st.session_state:
        st.session_state.keyboard_nav = {
            'last_key': None,
            'nav_direction': None,
            'input_focused': True
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
    """Main application function with enhanced UI and keyboard navigation."""
    st.set_page_config(
        page_title="Enhanced Python Terminal",
        page_icon="🐍",
        layout="wide",
        initial_sidebar_state="collapsed"
    )

    # Initialize session state
    initialize_session_state()

    # Authentic Terminal CSS - Real Terminal Appearance
    st.markdown("""
    <style>
    /* Hide Streamlit default elements */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
    .stApp > header {visibility: hidden;}
    .stApp > footer {visibility: hidden;}
    
    /* Full screen terminal */
    .stApp {
        background: #000000;
        color: #00ff00;
    }
    
    .main .block-container {
        padding: 0;
        max-width: 100%;
    }
    
    /* Terminal Window */
    .terminal-window {
        background: #1e1e1e;
        border: 1px solid #333;
        border-radius: 8px;
        box-shadow: 0 8px 32px rgba(0, 0, 0, 0.8);
        margin: 0;
        padding: 0;
        font-family: 'Consolas', 'Monaco', 'Courier New', 'Lucida Console', monospace;
        font-size: 14px;
        line-height: 1.2;
        min-height: 100vh;
        display: flex;
        flex-direction: column;
    }
    
    /* Terminal Title Bar */
    .terminal-titlebar {
        background: linear-gradient(to bottom, #3c3c3c, #2d2d2d);
        border-bottom: 1px solid #555;
        padding: 8px 12px;
        display: flex;
        justify-content: space-between;
        align-items: center;
        border-radius: 8px 8px 0 0;
    }
    
    .terminal-titlebar-left {
        display: flex;
        align-items: center;
        gap: 8px;
    }
    
    .terminal-buttons {
        display: flex;
        gap: 6px;
    }
    
    .terminal-button {
        width: 12px;
        height: 12px;
        border-radius: 50%;
        border: none;
        cursor: pointer;
    }
    
    .terminal-button.close { background: #ff5f57; }
    .terminal-button.minimize { background: #ffbd2e; }
    .terminal-button.maximize { background: #28ca42; }
    
    .terminal-title {
        color: #ffffff;
        font-size: 13px;
        font-weight: normal;
        margin-left: 10px;
    }
    
    .terminal-status {
        color: #888;
        font-size: 11px;
    }
    
    /* Terminal Content */
    .terminal-content {
        background: #000000;
        color: #00ff00;
        padding: 20px;
        flex: 1;
        overflow-y: auto;
        min-height: 60vh;
        max-height: 70vh;
        border: none;
    }
    
    .terminal-output {
        color: #00ff00;
        white-space: pre-wrap;
        margin: 0;
        padding: 0;
        line-height: 1.3;
        font-family: 'Consolas', 'Monaco', 'Courier New', 'Lucida Console', monospace;
        font-size: 14px;
    }
    
    .terminal-output .prompt {
        color: #00ff00;
        font-weight: bold;
    }
    
    .terminal-output .command {
        color: #ffffff;
    }
    
    .terminal-output .output {
        color: #cccccc;
    }
    
    .terminal-output .error {
        color: #ff6b6b;
    }
    
    .terminal-output .success {
        color: #51cf66;
    }
    
    /* Terminal Input Area */
    .terminal-input-area {
        background: #000000;
        border-top: 1px solid #333;
        padding: 15px 20px;
        display: flex;
        align-items: center;
        gap: 10px;
    }
    
    .terminal-prompt {
        color: #00ff00;
        font-weight: bold;
        font-family: 'Consolas', 'Monaco', 'Courier New', 'Lucida Console', monospace;
        font-size: 14px;
        white-space: nowrap;
        min-width: 200px;
    }
    
    /* Input Field Styling */
    .stTextInput > div > div > input {
        background: transparent !important;
        color: #00ff00 !important;
        border: none !important;
        font-family: 'Consolas', 'Monaco', 'Courier New', 'Lucida Console', monospace !important;
        font-size: 14px !important;
        padding: 0 !important;
        margin: 0 !important;
        outline: none !important;
        box-shadow: none !important;
        caret-color: #00ff00 !important;
    }
    
    .stTextInput > div > div > input:focus {
        border: none !important;
        box-shadow: none !important;
        outline: none !important;
    }
    
    /* Hide Streamlit input styling */
    .stTextInput > div {
        background: transparent !important;
        border: none !important;
    }
    
    .stTextInput > div > div {
        background: transparent !important;
        border: none !important;
    }
    
    /* Command Suggestions */
    .command-suggestions {
        background: #1a1a1a;
        border: 1px solid #333;
        border-radius: 4px;
        padding: 10px;
        margin: 10px 0;
        display: flex;
        flex-wrap: wrap;
        gap: 8px;
    }
    
    .suggestion-item {
        background: #2d2d2d;
        color: #00ff00;
        padding: 4px 8px;
        border-radius: 3px;
        cursor: pointer;
        font-size: 12px;
        font-family: 'Consolas', 'Monaco', 'Courier New', 'Lucida Console', monospace;
        border: 1px solid #444;
        transition: all 0.2s;
    }
    
    .suggestion-item:hover {
        background: #3d3d3d;
        border-color: #00ff00;
    }
    
    /* Control Buttons */
    .terminal-controls {
        background: #1a1a1a;
        border-top: 1px solid #333;
        padding: 10px 20px;
        display: flex;
        flex-wrap: wrap;
        gap: 8px;
        align-items: center;
    }
    
    .control-section {
        display: flex;
        gap: 8px;
        align-items: center;
        margin-right: 20px;
    }
    
    .control-label {
        color: #888;
        font-size: 11px;
        font-family: 'Consolas', 'Monaco', 'Courier New', 'Lucida Console', monospace;
        margin-right: 5px;
    }
    
    .stButton > button {
        background: #2d2d2d !important;
        color: #00ff00 !important;
        border: 1px solid #444 !important;
        font-family: 'Consolas', 'Monaco', 'Courier New', 'Lucida Console', monospace !important;
        font-size: 11px !important;
        padding: 4px 8px !important;
        border-radius: 3px !important;
        transition: all 0.2s !important;
    }
    
    .stButton > button:hover {
        background: #3d3d3d !important;
        border-color: #00ff00 !important;
    }
    
    /* Quick Commands */
    .quick-commands {
        display: flex;
        flex-wrap: wrap;
        gap: 6px;
        margin: 10px 0;
    }
    
    .quick-cmd {
        background: #1e3a8a;
        color: #60a5fa;
        padding: 3px 6px;
        border-radius: 2px;
        cursor: pointer;
        font-size: 10px;
        font-family: 'Consolas', 'Monaco', 'Courier New', 'Lucida Console', monospace;
        border: 1px solid #1e40af;
        transition: all 0.2s;
    }
    
    .quick-cmd:hover {
        background: #1d4ed8;
        border-color: #60a5fa;
    }
    
    /* Keyboard Hint */
    .keyboard-hint {
        background: #1e3a8a;
        color: #60a5fa;
        padding: 4px 8px;
        border-radius: 2px;
        font-size: 10px;
        font-family: 'Consolas', 'Monaco', 'Courier New', 'Lucida Console', monospace;
        margin: 5px 0;
        border: 1px solid #1e40af;
    }
    
    /* Form Styling */
    .command-form {
        background: transparent;
        padding: 0;
        border: none;
    }
    
    /* Scrollbar Styling */
    .terminal-content::-webkit-scrollbar {
        width: 8px;
    }
    
    .terminal-content::-webkit-scrollbar-track {
        background: #1a1a1a;
    }
    
    .terminal-content::-webkit-scrollbar-thumb {
        background: #444;
        border-radius: 4px;
    }
    
    .terminal-content::-webkit-scrollbar-thumb:hover {
        background: #555;
    }
    
    /* Cursor Blink Effect */
    @keyframes blink {
        0%, 50% { opacity: 1; }
        51%, 100% { opacity: 0; }
    }
    
    .terminal-cursor {
        animation: blink 1s infinite;
    }
    
    /* Welcome Message Styling */
    .welcome-message {
        color: #00ff00;
        font-family: 'Consolas', 'Monaco', 'Courier New', 'Lucida Console', monospace;
        line-height: 1.4;
    }
    
    .welcome-message .title {
        color: #ffffff;
        font-weight: bold;
    }
    
    .welcome-message .feature {
        color: #cccccc;
    }
    
    .welcome-message .shortcut {
        color: #60a5fa;
    }
    
    .welcome-message .example {
        color: #ffd43b;
    }
    </style>
    """, unsafe_allow_html=True)

    # Authentic Terminal Window
    st.markdown('<div class="terminal-window">', unsafe_allow_html=True)

    # Terminal Title Bar (like macOS Terminal)
    st.markdown(f"""
    <div class="terminal-titlebar">
        <div class="terminal-titlebar-left">
            <div class="terminal-buttons">
                <div class="terminal-button close"></div>
                <div class="terminal-button minimize"></div>
                <div class="terminal-button maximize"></div>
            </div>
            <div class="terminal-title">Terminal — Enhanced Python Terminal</div>
        </div>
        <div class="terminal-status">
            Commands: {len(st.session_state.command_history.get_history())} | 
            CWD: {os.path.basename(st.session_state.cwd)} | 
            NLP: Ready
        </div>
    </div>
    """, unsafe_allow_html=True)

    # Terminal Content Area
    st.markdown('<div class="terminal-content">', unsafe_allow_html=True)

    # Welcome message with authentic terminal styling
    if st.session_state.show_welcome and not st.session_state.terminal_output:
        st.markdown("""
        <div class="welcome-message">
        <span class="title">🚀 Enhanced Python Terminal with Advanced NLP</span><br><br>
        <span class="feature">Features:</span><br>
        • Full file system navigation (ls, cd, mkdir, touch, cp, mv, rm)<br>
        • System monitoring (cpu, mem, ps, disk)<br>
        • Advanced Natural Language Processing (!nlp commands)<br>
        • Keyboard navigation (UP/DOWN arrows for history)<br>
        • Smart command suggestions with TAB completion<br>
        • Cross-platform compatibility<br>
        • Form-based input with proper command handling<br><br>
        <span class="shortcut">Keyboard Shortcuts:</span><br>
        • ↑/↓ Arrow Keys: Navigate command history<br>
        • TAB: Auto-complete with first suggestion<br>
        • ENTER: Execute command<br><br>
        <span class="example">Try:</span><br>
        • 'help' for all commands<br>
        • '!nlp show me the files' for NLP<br>
        • '!nlp create a new file called test.txt'<br>
        • '!nlp go to home directory'<br>
        </div>
        """, unsafe_allow_html=True)

    # Display terminal output with authentic styling
    for output in st.session_state.terminal_output:
        # Parse output for different types
        if "Error:" in output or "error" in output.lower():
            st.markdown(
                f'<div class="terminal-output error">{output}</div>', unsafe_allow_html=True)
        elif "Success:" in output or "✓" in output:
            st.markdown(
                f'<div class="terminal-output success">{output}</div>', unsafe_allow_html=True)
        elif output.startswith("user@python-terminal:"):
            # Command line
            st.markdown(
                f'<div class="terminal-output"><span class="prompt">{output.split("$")[0]}$</span><span class="command">{output.split("$")[1] if "$" in output else ""}</span></div>', unsafe_allow_html=True)
        else:
            st.markdown(
                f'<div class="terminal-output output">{output}</div>', unsafe_allow_html=True)

    st.markdown('</div>', unsafe_allow_html=True)  # Close terminal-content

    # Terminal Input Area (like real terminal)
    st.markdown('<div class="terminal-input-area">', unsafe_allow_html=True)

    # Command input form with authentic terminal structure
    with st.form("enhanced_terminal_form", clear_on_submit=False):
        # Input field with prompt (like real terminal)
        col1, col2 = st.columns([1, 4])

        with col1:
            st.markdown(f'<div class="terminal-prompt">{get_prompt(st.session_state.cwd)}</div>',
                        unsafe_allow_html=True)

        with col2:
            command_input = st.text_input(
                "Command Input",
                value=st.session_state.current_input,
                placeholder="",
                key="enhanced_command_input",
                label_visibility="collapsed"
            )

        # Form buttons (hidden in authentic terminal)
        submit_button = st.form_submit_button(
            "Execute", type="primary", key="submit_hidden")
        clear_button = st.form_submit_button("Clear", key="clear_hidden")
        help_button = st.form_submit_button("Help", key="help_hidden")
        history_button = st.form_submit_button("History", key="history_hidden")
        nlp_button = st.form_submit_button("NLP Help", key="nlp_hidden")

    st.markdown('</div>', unsafe_allow_html=True)  # Close terminal-input-area

    # Terminal Controls (like real terminal)
    st.markdown('<div class="terminal-controls">', unsafe_allow_html=True)

    # History Navigation
    st.markdown('<div class="control-section">', unsafe_allow_html=True)
    st.markdown('<span class="control-label">History:</span>',
                unsafe_allow_html=True)

    col1, col2, col3 = st.columns(3)

    with col1:
        if st.button("↑ Prev", key="hist_up_btn"):
            handle_history_navigation("up")
            st.rerun()

    with col2:
        if st.button("↓ Next", key="hist_down_btn"):
            handle_history_navigation("down")
            st.rerun()

    with col3:
        if st.button("📜 History", key="history_btn"):
            history = st.session_state.command_history.get_history()
            if history:
                add_to_output("📜 Command History:")
                for i, cmd in enumerate(history[-10:], 1):
                    add_to_output(f"  {i}. {cmd}")
            else:
                add_to_output("No command history yet.")
            st.rerun()

    st.markdown('</div>', unsafe_allow_html=True)

    # Quick Commands
    st.markdown('<div class="control-section">', unsafe_allow_html=True)
    st.markdown('<span class="control-label">Quick:</span>',
                unsafe_allow_html=True)

    col1, col2, col3, col4, col5 = st.columns(5)

    with col1:
        if st.button("📁 PWD", key="pwd_btn"):
            handle_command("pwd")
            st.rerun()

    with col2:
        if st.button("🏠 Home", key="home_btn"):
            handle_command("cd ~")
            st.rerun()

    with col3:
        if st.button("🧹 Clear", key="clear_btn"):
            clear_terminal()
            st.session_state.current_input = ""
            st.rerun()

    with col4:
        if st.button("❓ Help", key="help_btn"):
            handle_command("help")
            st.rerun()

    with col5:
        if st.button("🧠 NLP", key="nlp_btn"):
            handle_command("!nlp help")
            st.rerun()

    st.markdown('</div>', unsafe_allow_html=True)

    st.markdown('</div>', unsafe_allow_html=True)  # Close terminal-controls

    # Command suggestions (appears below input like real terminal)
    if command_input and len(command_input) > 0:
        suggestions = get_suggestions(command_input)
        if suggestions:
            st.markdown('<div class="command-suggestions">',
                        unsafe_allow_html=True)
            st.markdown(
                '<span style="color: #888; font-size: 11px;">Suggestions: </span>', unsafe_allow_html=True)
            for suggestion in suggestions:
                if st.button(suggestion, key=f"enhanced_suggest_{suggestion}", help=f"Use '{suggestion}'"):
                    st.session_state.current_input = suggestion
                    st.rerun()
            st.markdown('</div>', unsafe_allow_html=True)

    # Quick Commands (like terminal shortcuts)
    st.markdown('<div class="quick-commands">', unsafe_allow_html=True)
    st.markdown('<span style="color: #888; font-size: 11px;">Quick: </span>',
                unsafe_allow_html=True)

    quick_commands = [
        ("ls -la", "List files"),
        ("touch test.txt", "Create file"),
        ("mkdir test_dir", "Create dir"),
        ("cpu", "CPU usage"),
        ("mem", "Memory"),
        ("ps", "Processes"),
        ("!nlp help", "NLP help"),
        ("help", "All commands")
    ]

    for cmd, help_text in quick_commands:
        if st.button(cmd, key=f"enhanced_quick_{cmd.replace(' ', '_')}", help=help_text):
            handle_command(cmd)
            st.rerun()

    st.markdown('</div>', unsafe_allow_html=True)

    # Enhanced JavaScript for authentic terminal behavior
    st.markdown("""
    <script>
    document.addEventListener('DOMContentLoaded', function() {
        const input = document.querySelector('input[aria-label="Command Input"]');
        if (input) {
            // Focus the input field (like real terminal)
            input.focus();
            
            // Add cursor blink effect
            input.style.caretColor = '#00ff00';
            
            input.addEventListener('keydown', function(e) {
                if (e.key === 'ArrowUp') {
                    e.preventDefault();
                    // Trigger up navigation
                    const upBtn = document.querySelector('button[data-testid="baseButton-secondary"]');
                    if (upBtn && upBtn.textContent.includes('↑ Prev')) {
                        upBtn.click();
                    }
                } else if (e.key === 'ArrowDown') {
                    e.preventDefault();
                    // Trigger down navigation
                    const downBtn = document.querySelectorAll('button[data-testid="baseButton-secondary"]');
                    for (let btn of downBtn) {
                        if (btn.textContent && btn.textContent.includes('↓ Next')) {
                            btn.click();
                            break;
                        }
                    }
                } else if (e.key === 'Tab') {
                    e.preventDefault();
                    // Auto-complete with first suggestion
                    const suggestions = document.querySelectorAll('button[data-testid="baseButton-secondary"]');
                    for (let btn of suggestions) {
                        if (btn.textContent && btn.textContent.includes('suggest_')) {
                            btn.click();
                            break;
                        }
                    }
                } else if (e.key === 'Enter') {
                    // Let the form handle submission
                    return true;
                }
            });
            
            // Keep focus on input (like real terminal)
            input.addEventListener('blur', function() {
                setTimeout(() => input.focus(), 100);
            });
            
            // Add terminal-like cursor
            input.style.cursor = 'text';
        }
        
        // Add terminal window behavior
        const terminalWindow = document.querySelector('.terminal-window');
        if (terminalWindow) {
            terminalWindow.style.cursor = 'default';
        }
    });
    </script>
    """, unsafe_allow_html=True)

    st.markdown('</div>', unsafe_allow_html=True)  # Close terminal-window

    # Handle form submissions (authentic terminal behavior)
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
            add_to_output("📜 Command History:")
            for i, cmd in enumerate(history[-10:], 1):
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
