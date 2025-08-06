#!/usr/bin/env python3
"""
Interactive installation script for Common Tool MCP Server.

This script helps users install and set up the Common Tool MCP Server
with proper configuration for their environment.
"""

import os
import platform
import subprocess
import sys
from pathlib import Path


def run_command(command: str, check: bool = True) -> subprocess.CompletedProcess:
    """Run a shell command and return the result."""
    print(f"Running: {command}")
    result = subprocess.run(
        command,
        shell=True,
        capture_output=True,
        text=True,
        check=False
    )
    
    if check and result.returncode != 0:
        print(f"Error: Command failed with return code {result.returncode}")
        print(f"STDOUT: {result.stdout}")
        print(f"STDERR: {result.stderr}")
        sys.exit(1)
    
    return result


def check_python_version():
    """Check if Python version is compatible."""
    version = sys.version_info
    if version.major < 3 or (version.major == 3 and version.minor < 8):
        print("❌ Python 3.8 or higher is required")
        print(f"Current version: {version.major}.{version.minor}.{version.micro}")
        sys.exit(1)
    
    print(f"✅ Python {version.major}.{version.minor}.{version.micro} is compatible")


def check_pip():
    """Check if pip is available."""
    try:
        result = run_command("pip --version", check=False)
        if result.returncode == 0:
            print("✅ pip is available")
            return "pip"
    except FileNotFoundError:
        pass
    
    try:
        result = run_command("pip3 --version", check=False)
        if result.returncode == 0:
            print("✅ pip3 is available")
            return "pip3"
    except FileNotFoundError:
        pass
    
    print("❌ pip is not available. Please install pip first.")
    sys.exit(1)


def install_package(pip_cmd: str, dev_mode: bool = False):
    """Install the package."""
    print("\n📦 Installing Common Tool MCP Server...")
    
    if dev_mode:
        # Install in development mode with dev dependencies
        run_command(f"{pip_cmd} install -e .[dev]")
        print("✅ Installed in development mode with dev dependencies")
        
        # Install pre-commit hooks
        try:
            run_command("pre-commit install")
            print("✅ Pre-commit hooks installed")
        except subprocess.CalledProcessError:
            print("⚠️ Failed to install pre-commit hooks (optional)")
    else:
        # Install in normal mode
        run_command(f"{pip_cmd} install -e .")
        print("✅ Installed in normal mode")


def test_installation():
    """Test if installation was successful."""
    print("\n🧪 Testing installation...")
    
    try:
        result = run_command("common-tool-mcp-server --version", check=False)
        if result.returncode == 0:
            print("✅ Installation test successful")
            print(f"Version: {result.stdout.strip()}")
            return True
        else:
            print("❌ Installation test failed")
            print(f"Error: {result.stderr}")
            return False
    except Exception as e:
        print(f"❌ Installation test failed: {str(e)}")
        return False


def generate_vscode_config():
    """Generate VS Code MCP configuration."""
    config = {
        "mcpServers": {
            "common-tools": {
                "command": "common-tool-mcp-server",
                "args": []
            }
        }
    }
    
    config_dir = Path.home() / ".vscode"
    config_file = config_dir / "mcp_servers.json"
    
    try:
        config_dir.mkdir(exist_ok=True)
        
        # Read existing config if it exists
        existing_config = {}
        if config_file.exists():
            import json
            with open(config_file, 'r') as f:
                existing_config = json.load(f)
        
        # Merge configurations
        if "mcpServers" not in existing_config:
            existing_config["mcpServers"] = {}
        
        existing_config["mcpServers"]["common-tools"] = config["mcpServers"]["common-tools"]
        
        # Write updated config
        import json
        with open(config_file, 'w') as f:
            json.dump(existing_config, f, indent=2)
        
        print(f"✅ VS Code configuration written to: {config_file}")
        return True
        
    except Exception as e:
        print(f"⚠️ Failed to write VS Code configuration: {str(e)}")
        return False


def show_usage_info():
    """Show usage information."""
    print("\n🎯 Usage Information:")
    print("─" * 50)
    print("Start the server:")
    print("  common-tool-mcp-server")
    print()
    print("Start with debug logging:")
    print("  common-tool-mcp-server --log-level DEBUG")
    print()
    print("Show help:")
    print("  common-tool-mcp-server --help")
    print()
    print("Run example:")
    print("  python example.py")
    print()
    print("📚 For more information, see README.md")


def main():
    """Main installation function."""
    print("🔧 Common Tool MCP Server - Installation Script")
    print("=" * 60)
    
    # Check system requirements
    print("\n🔍 Checking system requirements...")
    check_python_version()
    pip_cmd = check_pip()
    
    # Get installation preferences
    print("\n⚙️ Installation Options:")
    dev_mode = input("Install in development mode? (y/N): ").lower().startswith('y')
    vscode_config = input("Generate VS Code MCP configuration? (Y/n): ").lower() != 'n'
    
    # Install the package
    try:
        install_package(pip_cmd, dev_mode)
        
        # Test installation
        if test_installation():
            print("\n🎉 Installation completed successfully!")
            
            # Generate VS Code config if requested
            if vscode_config:
                generate_vscode_config()
            
            # Show usage information
            show_usage_info()
            
        else:
            print("\n❌ Installation completed but tests failed")
            print("Please check the installation manually")
            
    except Exception as e:
        print(f"\n❌ Installation failed: {str(e)}")
        sys.exit(1)


if __name__ == "__main__":
    main() 