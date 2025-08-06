"""
Common Tool MCP Server

A Model Context Protocol (MCP) server that provides common system tools and utilities.
This server offers various system administration and utility commands through MCP,
making them available to AI assistants and other MCP clients.
"""

__version__ = "1.0.0"
__author__ = "Common Tool MCP Server Team"
__email__ = "your.email@example.com"

from .server import CommonToolMCPServer
from .types import (
    ProcessInfo,
    SystemInfo,
    FileInfo,
    NetworkInfo,
    DiskInfo,
)

__all__ = [
    "CommonToolMCPServer",
    "ProcessInfo",
    "SystemInfo", 
    "FileInfo",
    "NetworkInfo",
    "DiskInfo",
] 