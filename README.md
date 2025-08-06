# Common Tool MCP Server

A comprehensive Model Context Protocol (MCP) server that provides common system tools and utilities for AI assistants and other MCP clients. This server offers a wide range of system administration capabilities including process management, file operations, system monitoring, and command execution.

## 🚀 Features

### Process Management
- **List Processes**: Get detailed information about running processes with filtering options
- **Kill Process**: Terminate processes by PID with graceful or forced termination
- **Kill by Name**: Terminate all processes matching a specific name

### System Information
- **System Info**: Comprehensive system details (CPU, memory, platform, etc.)
- **Disk Usage**: Monitor disk space usage across all mounted drives
- **Network Information**: Get network interface details and statistics
- **Listening Ports**: View active network ports and associated processes

### File Operations
- **List Files**: Browse directories with options for hidden files and recursive listing
- **Read Files**: Read file contents with customizable encoding
- **Write Files**: Create or modify files with append mode support

### Command Execution
- **Execute Commands**: Run shell commands with timeout and working directory control
- **Cross-platform**: Works on Windows, macOS, and Linux

### Network Tools
- **Ping**: Test connectivity to hosts with configurable packet count

### Environment Management
- **Environment Variables**: View, get, and set environment variables

## 📦 Installation

### Prerequisites
- Python 3.8 or higher
- pip package manager

### Install from Source

```bash
# Clone the repository
git clone <repository-url>
cd CommonToolMcp

# Install in development mode
pip install -e .

# Or install with development dependencies
pip install -e ".[dev]"
```

### Quick Install

```bash
pip install common-tool-mcp-server
```

## 🎯 Usage

### Starting the Server

```bash
# Start with default settings (stdio transport)
common-tool-mcp-server

# Start with debug logging
common-tool-mcp-server --log-level DEBUG

# Start HTTP server
common-tool-mcp-server --transport http --host 0.0.0.0 --port 8080

# Start SSE server
common-tool-mcp-server --transport sse --port 8090

# Custom server name
common-tool-mcp-server --name "My Common Tools Server"

# Show help
common-tool-mcp-server --help
```

### Transport Options

The server supports multiple transport protocols:

- **stdio**: Default mode for MCP client integration
- **http**: HTTP-based transport for web applications
- **sse**: Server-Sent Events transport for real-time applications

Command line options:
- `--transport {stdio,http,sse}`: Choose transport protocol
- `--host HOST`: Host address for http/sse (default: 127.0.0.1)
- `--port PORT`: Port number for http/sse (default: 8000)
- `--name NAME`: Custom server name

### VS Code Integration

Add the server to your VS Code MCP settings:

```json
{
  "mcpServers": {
    "common-tools": {
      "command": "common-tool-mcp-server",
      "args": []
    }
  }
}
```

### Available Tools

#### Process Management

**list_processes**
```json
{
  "name": "list_processes",
  "arguments": {
    "filter_name": "python",          // Optional: filter by process name
    "filter_user": "username",        // Optional: filter by username
    "include_details": true           // Optional: include CPU/memory details
  }
}
```

**kill_process**
```json
{
  "name": "kill_process", 
  "arguments": {
    "pid": 1234,                      // Required: process ID
    "force": false                    // Optional: use SIGKILL instead of SIGTERM
  }
}
```

**kill_processes_by_name**
```json
{
  "name": "kill_processes_by_name",
  "arguments": {
    "name": "chrome",                 // Required: process name
    "force": false                    // Optional: force kill
  }
}
```

#### System Information

**get_system_info**
```json
{
  "name": "get_system_info",
  "arguments": {}
}
```

**get_disk_usage**
```json
{
  "name": "get_disk_usage",
  "arguments": {
    "path": "/"                       // Optional: specific path (default: all drives)
  }
}
```

**get_network_info**
```json
{
  "name": "get_network_info",
  "arguments": {}
}
```

**get_listening_ports**
```json
{
  "name": "get_listening_ports", 
  "arguments": {}
}
```

#### File Operations

**list_files**
```json
{
  "name": "list_files",
  "arguments": {
    "directory": "/path/to/dir",      // Optional: directory path (default: ".")
    "include_hidden": false,          // Optional: include hidden files
    "recursive": false                // Optional: recursive listing
  }
}
```

**read_file**
```json
{
  "name": "read_file",
  "arguments": {
    "filepath": "/path/to/file.txt",  // Required: file path
    "encoding": "utf-8"               // Optional: file encoding
  }
}
```

**write_file**
```json
{
  "name": "write_file",
  "arguments": {
    "filepath": "/path/to/file.txt",  // Required: file path
    "content": "Hello, World!",       // Required: content to write
    "encoding": "utf-8",              // Optional: file encoding
    "append": false                   // Optional: append mode
  }
}
```

#### Command Execution

**execute_command**
```json
{
  "name": "execute_command",
  "arguments": {
    "command": "ls -la",              // Required: command to run
    "cwd": "/working/directory",      // Optional: working directory
    "timeout": 30.0,                  // Optional: timeout in seconds
    "shell": true                     // Optional: run in shell
  }
}
```

#### Network Tools

**ping_host**
```json
{
  "name": "ping_host",
  "arguments": {
    "host": "google.com",             // Required: hostname or IP
    "count": 4                        // Optional: number of ping packets
  }
}
```

#### Environment Variables

**get_environment_variables**
```json
{
  "name": "get_environment_variables",
  "arguments": {}
}
```

**get_environment_variable**
```json
{
  "name": "get_environment_variable",
  "arguments": {
    "name": "PATH"                    // Required: variable name
  }
}
```

**set_environment_variable**
```json
{
  "name": "set_environment_variable",
  "arguments": {
    "name": "MY_VAR",                 // Required: variable name
    "value": "my_value"               // Required: variable value
  }
}
```

### Available Resources

The server provides several system resources accessible via URI:

- `system://info` - Current system information
- `system://processes` - Running processes list
- `system://disks` - Disk usage information  
- `system://network` - Network interface information
- `system://ports` - Listening ports information
- `system://environment` - Environment variables

## 🛠️ Development

### Setup Development Environment

```bash
# Clone the repository
git clone <repository-url>
cd CommonToolMcp

# Install development dependencies
make install-dev

# Install pre-commit hooks
pre-commit install
```

### Development Commands

```bash
# Run tests
make test

# Run tests with coverage
make test-cov

# Lint code
make lint

# Format code
make format

# Type check
make type-check

# Run all checks
make check

# Clean build artifacts
make clean

# Build distribution
make build
```

### Running Tests

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=common_tool_mcp_server

# Run specific test file
pytest tests/test_system_client.py

# Run specific test
pytest tests/test_system_client.py::TestProcessManagement::test_list_processes
```

### Code Quality

The project uses several tools to maintain code quality:

- **Black**: Code formatting
- **isort**: Import sorting
- **flake8**: Linting
- **mypy**: Type checking
- **pytest**: Testing
- **pre-commit**: Git hooks

### Project Structure

```
CommonToolMcp/
├── common_tool_mcp_server/     # Main package
│   ├── __init__.py            # Package initialization
│   ├── main.py                # Command-line entry point
│   ├── server.py              # MCP server implementation
│   ├── system_client.py       # System tools client
│   ├── types.py               # Type definitions
│   └── py.typed               # Type hint marker
├── tests/                     # Test suite
│   ├── __init__.py
│   └── test_system_client.py  # Client tests
├── pyproject.toml            # Project configuration
├── requirements.txt          # Dependencies
├── requirements-dev.txt      # Development dependencies
├── README.md                 # This file
├── LICENSE                   # MIT license
├── Makefile                  # Development tasks
├── .pre-commit-config.yaml   # Pre-commit configuration
└── .gitignore               # Git ignore rules
```

## 🔒 Security Considerations

This server provides powerful system access capabilities. When using it:

1. **Process Management**: Be careful with kill operations, especially force kills
2. **File Operations**: Ensure proper permissions and avoid overwriting critical files
3. **Command Execution**: Validate commands to prevent unintended system changes
4. **Environment Variables**: Be cautious when setting variables that might affect system behavior

## 🐛 Troubleshooting

### Common Issues

**Permission Errors**
- Ensure the server has appropriate permissions for the operations you're trying to perform
- Some process operations may require elevated privileges

**Import Errors**
- Make sure all dependencies are installed: `pip install -e .`
- Check Python version compatibility (3.8+)

**Platform Compatibility**
- Some commands may behave differently across platforms
- Network and process management features are cross-platform compatible

### Debug Mode

Run with debug logging to get detailed information:

```bash
common-tool-mcp-server --log-level DEBUG
```

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request. For major changes, please open an issue first to discuss what you would like to change.

### Development Workflow

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Make your changes
4. Run tests and linting (`make check`)
5. Commit your changes (`git commit -m 'Add amazing feature'`)
6. Push to the branch (`git push origin feature/amazing-feature`)
7. Open a Pull Request

## 📞 Support

If you encounter any problems or have questions, please:

1. Check the [troubleshooting section](#-troubleshooting)
2. Search existing [issues](https://github.com/yourusername/common-tool-mcp-server/issues)
3. Create a new issue with detailed information about your problem

## 🔄 Changelog

### Version 1.0.0
- Initial release
- Process management tools
- System information gathering
- File operations
- Command execution
- Network tools
- Environment variable management
- Cross-platform support
- Comprehensive test suite 