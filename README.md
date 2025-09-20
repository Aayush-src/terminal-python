# 🐍 Python Terminal

A web-based custom terminal built with Streamlit that provides a clean, modern interface for file operations and system monitoring.

## ✨ Features

- **File Operations**: `ls`, `cd`, `pwd`, `mkdir`, `rm` with full argument support
- **System Monitoring**: `cpu`, `mem`, `ps`, `disk` commands using psutil
- **Command History**: Navigate through previous commands
- **NLP Integration**: Natural language command processing (experimental)
- **Cross-Platform**: Works on Windows, macOS, and Linux
- **Security**: Safe file operations with path restrictions
- **Modern UI**: Clean, terminal-inspired interface

## 🚀 Quick Start

1. **Install Dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

2. **Run the Application**:
   ```bash
   streamlit run app.py
   ```

3. **Open in Browser**: The app will automatically open at `http://localhost:8501`

## 📁 Project Structure

```
project_root/
├── app.py                    # Main Streamlit application
├── terminal_backend.py       # Command executor and routing
├── commands/
│   ├── file_ops.py          # File and directory operations
│   └── system_ops.py        # System monitoring commands
├── utils/
│   ├── history.py           # Command history management
│   └── helpers.py           # Utility functions
├── nlp/
│   └── interpreter.py       # NLP command interpreter
├── requirements.txt         # Python dependencies
└── README.md               # This file
```

## 🎯 Available Commands

### File Operations
- `ls [options] [directory]` - List directory contents
  - Options: `-l` (long format), `-a` (show hidden)
- `cd [directory]` - Change directory
- `pwd` - Print working directory
- `mkdir <name>` - Create directory
- `rm [options] <name>` - Remove file or directory
  - Options: `-r` (recursive for directories)

### System Monitoring
- `cpu` - Show CPU usage information
- `mem` - Show memory usage information
- `ps [options]` - Show running processes
  - Options: `-a` (show all), `<number>` (limit results)
- `disk` - Show disk usage information

### Special Commands
- `help` - Show help information
- `clear` - Clear the terminal
- `exit`/`quit` - Exit the terminal

### NLP Commands
- `!nlp <query>` - Natural language command processing
  - Example: `!nlp show me the files`
  - Example: `!nlp what's my current directory`

## 🔧 Architecture

The application follows a clean MVC-style architecture:

- **Model**: Command implementations in `commands/` directory
- **View**: Streamlit UI in `app.py`
- **Controller**: Command routing in `terminal_backend.py`

## 🛡️ Security Features

- **Path Restrictions**: All file operations are restricted to safe directories
- **Input Validation**: Commands are validated before execution
- **Error Handling**: Comprehensive error handling prevents crashes
- **Safe Operations**: Dangerous system operations are prevented

## 🎨 UI Features

- **Terminal Styling**: Authentic terminal look and feel
- **Command History**: Navigate through previous commands
- **Quick Commands**: One-click access to common operations
- **Real-time Output**: Live command execution and output display
- **Responsive Design**: Works on different screen sizes

## 🔮 Future Enhancements

- **Advanced NLP**: Integration with language models for better natural language processing
- **Custom Themes**: Multiple terminal themes and color schemes
- **Plugin System**: Extensible command system for custom operations
- **File Editor**: Built-in file editing capabilities
- **Remote Connections**: SSH and remote terminal support

## 🐛 Troubleshooting

### Common Issues

1. **Permission Errors**: Ensure the application has proper file system permissions
2. **Port Already in Use**: Change the port with `streamlit run app.py --server.port 8502`
3. **Missing Dependencies**: Run `pip install -r requirements.txt`

### Getting Help

- Use the `help` command in the terminal
- Check the quick command buttons in the sidebar
- Review the error messages for specific issues

## 📝 License

This project is open source and available under the MIT License.

## 🤝 Contributing

Contributions are welcome! Please feel free to submit issues and pull requests.

---

**Happy Terminal-ing! 🚀**
