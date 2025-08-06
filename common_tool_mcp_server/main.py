"""
Main entry point for the Common Tool MCP Server.
"""

import argparse
import asyncio
import logging
import sys

from .server import CommonToolMCPServer


def setup_logging(level: str = "INFO") -> None:
    """Set up logging configuration."""
    log_level = getattr(logging, level.upper(), logging.INFO)
    logging.basicConfig(
        level=log_level,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        handlers=[
            logging.StreamHandler(sys.stderr)
        ]
    )


def parse_args() -> argparse.Namespace:
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(
        description="Common Tool MCP Server - Provides system tools through MCP",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Run with stdio transport (default)
  common-tool-mcp-server
  
  # Run with debug logging
  common-tool-mcp-server --log-level DEBUG
  
  # Start HTTP server
  common-tool-mcp-server --transport http --host 0.0.0.0 --port 8080
  
  # Show version
  common-tool-mcp-server --version

Available Tools:
  Process Management:
    - list_processes: List running processes with optional filtering
    - kill_process: Kill a process by PID
    - kill_processes_by_name: Kill all processes with given name
  
  System Information:
    - get_system_info: Get comprehensive system information
    - get_disk_usage: Get disk usage information
    - get_network_info: Get network interface information
    - get_listening_ports: Get listening network ports
  
  File Operations:
    - list_files: List files and directories
    - read_file: Read file contents
    - write_file: Write content to file
  
  Command Execution:
    - execute_command: Execute shell commands
  
  Network Tools:
    - ping_host: Ping a host to test connectivity
  
  Environment Variables:
    - get_environment_variables: Get all environment variables
    - get_environment_variable: Get specific environment variable
    - set_environment_variable: Set environment variable

Available Resources:
  - system://info: Current system information
  - system://processes: Running processes list
  - system://disks: Disk usage information
  - system://network: Network interface information
  - system://ports: Listening ports information
  - system://environment: Environment variables
        """,
    )
    
    parser.add_argument(
        "--name",
        type=str,
        default="Common Tool MCP Server",
        help="Server name (default: 'Common Tool MCP Server')"
    )
    
    parser.add_argument(
        "--transport",
        type=str,
        choices=["stdio", "http", "sse"],
        default="stdio",
        help="Transport protocol (default: stdio)"
    )
    
    parser.add_argument(
        "--host",
        type=str,
        default="127.0.0.1",
        help="Host address for http/sse transport (default: 127.0.0.1)"
    )
    
    parser.add_argument(
        "--port",
        type=int,
        default=8000,
        help="Port number for http/sse transport (default: 8000)"
    )
    
    parser.add_argument(
        "--log-level",
        choices=["DEBUG", "INFO", "WARNING", "ERROR"],
        default="INFO",
        help="Set the logging level (default: INFO)",
    )
    
    parser.add_argument(
        "--version",
        action="version",
        version="common-tool-mcp-server 1.0.0",
    )
    
    return parser.parse_args()


async def main() -> None:
    """Main entry point."""
    args = parse_args()
    
    # Setup logging
    setup_logging(args.log_level)
    logger = logging.getLogger(__name__)
    
    try:
        # Create and run the server
        server = CommonToolMCPServer(name=args.name)
        
        print(f"Starting {args.name}...")
        print(f"Transport: {args.transport}")
        if args.transport in ["http", "sse"]:
            print(f"Address: {args.host}:{args.port}")
        
        await server.run(
            transport=args.transport,
            host=args.host,
            port=args.port
        )
        
    except KeyboardInterrupt:
        print("\nServer stopped by user.")
        sys.exit(0)
    except Exception as e:
        print(f"Error starting server: {e}", file=sys.stderr)
        sys.exit(1)


def sync_main() -> None:
    """Synchronous entry point for setuptools."""
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        pass


if __name__ == "__main__":
    sync_main() 
 