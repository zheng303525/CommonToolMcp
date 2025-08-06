"""
Common Tool MCP Server implementation using FastMCP.

This server provides various system tools and utilities through the Model Context Protocol (MCP).
It offers process management, system information, file operations, network tools, and command execution.
"""

import asyncio
import json
import logging
from typing import Any, Dict, List, Optional, Union
from dataclasses import asdict

from fastmcp import FastMCP, Context
from pydantic import BaseModel, Field

from .system_client import SystemToolsClient
from .types import (
    ProcessInfo,
    SystemInfo,
    DiskInfo,
    NetworkInfo,
    FileInfo,
    CommandResult,
    PortInfo,
    EnvironmentVariable,
)


# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class CommonToolMCPServer:
    """MCP Server for common system tools and utilities using FastMCP."""

    def __init__(self, name: str = "Common Tool MCP Server") -> None:
        """Initialize the server."""
        self.mcp = FastMCP(name)
        self.system_client = SystemToolsClient()
        self._register_tools()
        self._register_resources()

    def _register_tools(self) -> None:
        """Register system tools with the MCP server."""
        
        # Process Management Tools
        @self.mcp.tool
        async def list_processes(
            ctx: Context,
            filter_name: Optional[str] = None,
            filter_user: Optional[str] = None,
            include_details: bool = False
        ) -> Dict[str, Any]:
            """List running processes with optional filtering.
            
            Args:
                filter_name: Filter processes by name (partial match)
                filter_user: Filter processes by username  
                include_details: Include detailed process information (CPU, memory, etc.)
                ctx: MCP context
            """
            await ctx.info(f"Listing processes with filters: name={filter_name}, user={filter_user}")
            
            processes = await self.system_client.list_processes(
                filter_name=filter_name,
                filter_user=filter_user,
                include_details=include_details
            )
            
            result = [asdict(p) for p in processes]
            await ctx.info(f"Found {len(processes)} processes")
            
            return {
                "processes": result,
                "count": len(processes)
            }

        @self.mcp.tool
        async def kill_process(
            ctx: Context,
            pid: int,
            force: bool = False
        ) -> Dict[str, Any]:
            """Kill a process by PID.
            
            Args:
                pid: Process ID to kill
                force: Use force kill (SIGKILL) instead of graceful termination
                ctx: MCP context
            """
            await ctx.info(f"Killing process PID {pid} (force={force})")
            
            result = await self.system_client.kill_process(pid=pid, force=force)
            
            if result.success:
                await ctx.info(f"Successfully killed process {pid}")
            else:
                await ctx.error(f"Failed to kill process {pid}: {result.stderr}")
            
            return asdict(result)

        @self.mcp.tool
        async def kill_processes_by_name(
            ctx: Context,
            name: str,
            force: bool = False
        ) -> Dict[str, Any]:
            """Kill all processes with the given name.
            
            Args:
                name: Process name to kill
                force: Use force kill (SIGKILL) instead of graceful termination
                ctx: MCP context
            """
            await ctx.info(f"Killing processes by name '{name}' (force={force})")
            
            result = await self.system_client.kill_processes_by_name(name=name, force=force)
            
            if result.success:
                await ctx.info(f"Successfully killed processes: {result.stdout}")
            else:
                await ctx.error(f"Failed to kill processes: {result.stderr}")
            
            return asdict(result)

        # System Information Tools
        @self.mcp.tool
        async def get_system_info(ctx: Context) -> Dict[str, Any]:
            """Get comprehensive system information.
            
            Args:
                ctx: MCP context
            """
            await ctx.info("Getting system information")
            
            system_info = await self.system_client.get_system_info()
            
            await ctx.info(f"System: {system_info.platform} {system_info.platform_release}")
            
            return asdict(system_info)

        @self.mcp.tool
        async def get_disk_usage(
            ctx: Context,
            path: str = "/"
        ) -> Dict[str, Any]:
            """Get disk usage information.
            
            Args:
                path: Specific path to check (default: all mounted drives)
                ctx: MCP context
            """
            await ctx.info(f"Getting disk usage for path: {path}")
            
            disks = await self.system_client.get_disk_usage(path=path)
            
            result = [asdict(d) for d in disks]
            await ctx.info(f"Found {len(disks)} disk(s)")
            
            return {
                "disks": result,
                "count": len(disks)
            }

        @self.mcp.tool
        async def get_network_info(ctx: Context) -> Dict[str, Any]:
            """Get network interface information and statistics.
            
            Args:
                ctx: MCP context
            """
            await ctx.info("Getting network interface information")
            
            network_info = await self.system_client.get_network_info()
            
            result = [asdict(n) for n in network_info]
            await ctx.info(f"Found {len(network_info)} network interface(s)")
            
            return {
                "interfaces": result,
                "count": len(network_info)
            }

        @self.mcp.tool
        async def get_listening_ports(ctx: Context) -> Dict[str, Any]:
            """Get list of network ports currently listening.
            
            Args:
                ctx: MCP context
            """
            await ctx.info("Getting listening ports")
            
            ports = await self.system_client.get_listening_ports()
            
            result = [asdict(p) for p in ports]
            await ctx.info(f"Found {len(ports)} listening port(s)")
            
            return {
                "ports": result,
                "count": len(ports)
            }

        # File Operations Tools
        @self.mcp.tool
        async def list_files(
            ctx: Context,
            directory: str = ".",
            include_hidden: bool = False,
            recursive: bool = False
        ) -> Dict[str, Any]:
            """List files and directories.
            
            Args:
                directory: Directory to list (default: current directory)
                include_hidden: Include hidden files (starting with .)
                recursive: List files recursively
                ctx: MCP context
            """
            await ctx.info(f"Listing files in directory: {directory}")
            
            files = await self.system_client.list_files(
                directory=directory,
                include_hidden=include_hidden,
                recursive=recursive
            )
            
            result = [asdict(f) for f in files]
            await ctx.info(f"Found {len(files)} file(s)")
            
            return {
                "files": result,
                "count": len(files)
            }

        @self.mcp.tool
        async def read_file(
            ctx: Context,
            filepath: str,
            encoding: str = "utf-8"
        ) -> Dict[str, Any]:
            """Read the contents of a file.
            
            Args:
                filepath: Path to the file to read
                encoding: File encoding (default: utf-8)
                ctx: MCP context
            """
            await ctx.info(f"Reading file: {filepath}")
            
            try:
                content = await self.system_client.read_file(
                    filepath=filepath,
                    encoding=encoding
                )
                
                await ctx.info(f"Successfully read file: {filepath}")
                
                return {
                    "filepath": filepath,
                    "content": content,
                    "encoding": encoding,
                    "success": True
                }
                
            except Exception as e:
                error_msg = f"Failed to read file {filepath}: {str(e)}"
                await ctx.error(error_msg)
                
                return {
                    "filepath": filepath,
                    "content": "",
                    "encoding": encoding,
                    "success": False,
                    "error": str(e)
                }

        @self.mcp.tool
        async def write_file(
            ctx: Context,
            filepath: str,
            content: str,
            encoding: str = "utf-8",
            append: bool = False
        ) -> Dict[str, Any]:
            """Write content to a file.
            
            Args:
                filepath: Path to the file to write
                content: Content to write to the file
                encoding: File encoding (default: utf-8)
                append: Append to file instead of overwriting
                ctx: MCP context
            """
            mode = "append" if append else "write"
            await ctx.info(f"Writing to file: {filepath} (mode: {mode})")
            
            result = await self.system_client.write_file(
                filepath=filepath,
                content=content,
                encoding=encoding,
                append=append
            )
            
            if result.success:
                await ctx.info(f"Successfully wrote to file: {filepath}")
            else:
                await ctx.error(f"Failed to write to file: {result.stderr}")
            
            return asdict(result)

        # Command Execution Tools
        @self.mcp.tool
        async def execute_command(
            ctx: Context,
            command: str,
            cwd: Optional[str] = None,
            timeout: Optional[float] = None,
            shell: bool = True
        ) -> Dict[str, Any]:
            """Execute a shell command.
            
            Args:
                command: Command to execute
                cwd: Working directory for the command
                timeout: Timeout in seconds (default: no timeout)
                shell: Run command in shell (default: true)
                ctx: MCP context
            """
            await ctx.info(f"Executing command: {command}")
            
            result = await self.system_client.execute_command(
                command=command,
                cwd=cwd,
                timeout=timeout,
                shell=shell
            )
            
            if result.success:
                await ctx.info(f"Command executed successfully")
            else:
                await ctx.error(f"Command failed with return code {result.return_code}")
            
            return asdict(result)

        # Network Tools
        @self.mcp.tool
        async def ping_host(
            ctx: Context,
            host: str,
            count: int = 4
        ) -> Dict[str, Any]:
            """Ping a host to test connectivity.
            
            Args:
                host: Hostname or IP address to ping
                count: Number of ping packets to send (default: 4)
                ctx: MCP context
            """
            await ctx.info(f"Pinging host: {host} (count: {count})")
            
            result = await self.system_client.ping_host(host=host, count=count)
            
            if result.success:
                await ctx.info(f"Ping to {host} successful")
            else:
                await ctx.error(f"Ping to {host} failed")
            
            return asdict(result)

        # Environment Variable Tools
        @self.mcp.tool
        async def get_environment_variables(ctx: Context) -> Dict[str, Any]:
            """Get all environment variables.
            
            Args:
                ctx: MCP context
            """
            await ctx.info("Getting environment variables")
            
            env_vars = await self.system_client.get_environment_variables()
            
            result = [asdict(e) for e in env_vars]
            await ctx.info(f"Found {len(env_vars)} environment variable(s)")
            
            return {
                "variables": result,
                "count": len(env_vars)
            }

        @self.mcp.tool
        async def get_environment_variable(
            ctx: Context,
            name: str
        ) -> Dict[str, Any]:
            """Get a specific environment variable.
            
            Args:
                name: Environment variable name
                ctx: MCP context
            """
            await ctx.info(f"Getting environment variable: {name}")
            
            value = await self.system_client.get_environment_variable(name=name)
            
            result = {
                "name": name,
                "value": value,
                "exists": value is not None
            }
            
            if value is not None:
                await ctx.info(f"Environment variable {name} found")
            else:
                await ctx.info(f"Environment variable {name} not found")
            
            return result

        @self.mcp.tool
        async def set_environment_variable(
            ctx: Context,
            name: str,
            value: str
        ) -> Dict[str, Any]:
            """Set an environment variable (current session only).
            
            Args:
                name: Environment variable name
                value: Environment variable value
                ctx: MCP context
            """
            await ctx.info(f"Setting environment variable: {name}={value}")
            
            result = await self.system_client.set_environment_variable(name=name, value=value)
            
            if result.success:
                await ctx.info(f"Successfully set environment variable: {name}")
            else:
                await ctx.error(f"Failed to set environment variable: {result.stderr}")
            
            return asdict(result)

    def _register_resources(self) -> None:
        """Register system resources with the MCP server."""
        
        @self.mcp.resource("system://info")
        async def system_info_resource(ctx: Context) -> str:
            """Current system information resource."""
            await ctx.info("Providing system information resource")
            
            system_info = await self.system_client.get_system_info()
            return json.dumps(asdict(system_info), indent=2, default=str)

        @self.mcp.resource("system://processes")
        async def processes_resource(ctx: Context) -> str:
            """Running processes list resource."""
            await ctx.info("Providing processes resource")
            
            processes = await self.system_client.list_processes(include_details=True)
            return json.dumps([asdict(p) for p in processes], indent=2, default=str)

        @self.mcp.resource("system://disks")
        async def disks_resource(ctx: Context) -> str:
            """Disk usage information resource."""
            await ctx.info("Providing disk usage resource")
            
            disks = await self.system_client.get_disk_usage()
            return json.dumps([asdict(d) for d in disks], indent=2, default=str)

        @self.mcp.resource("system://network")
        async def network_resource(ctx: Context) -> str:
            """Network interface information resource."""
            await ctx.info("Providing network information resource")
            
            network_info = await self.system_client.get_network_info()
            return json.dumps([asdict(n) for n in network_info], indent=2, default=str)

        @self.mcp.resource("system://ports")
        async def ports_resource(ctx: Context) -> str:
            """Listening ports information resource."""
            await ctx.info("Providing listening ports resource")
            
            ports = await self.system_client.get_listening_ports()
            return json.dumps([asdict(p) for p in ports], indent=2, default=str)

        @self.mcp.resource("system://environment")
        async def environment_resource(ctx: Context) -> str:
            """Environment variables resource."""
            await ctx.info("Providing environment variables resource")
            
            env_vars = await self.system_client.get_environment_variables()
            return json.dumps([asdict(e) for e in env_vars], indent=2, default=str)

    async def run(
        self,
        transport: str = "stdio",
        host: str = "127.0.0.1",
        port: int = 8000,
    ) -> None:
        """Run the MCP server.
        
        Args:
            transport: Transport protocol ("stdio", "http", or "sse")
            host: Host address for http/sse transport
            port: Port number for http/sse transport
        """
        if transport == "stdio":
            await self.mcp.run("stdio")
        elif transport == "http":
            await self.mcp.run("http", host=host, port=port)
        elif transport == "sse":
            await self.mcp.run("sse", host=host, port=port)
        else:
            raise ValueError(f"Unsupported transport: {transport}") 