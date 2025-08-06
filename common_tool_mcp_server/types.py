"""
Type definitions for the Common Tool MCP Server.
"""

from dataclasses import dataclass
from typing import Dict, List, Optional, Any, Union
from datetime import datetime


@dataclass
class ProcessInfo:
    """Information about a system process."""
    
    pid: int
    name: str
    status: str
    username: str
    cpu_percent: float
    memory_percent: float
    memory_info_rss: int  # Resident Set Size in bytes
    memory_info_vms: int  # Virtual Memory Size in bytes
    create_time: datetime
    cmdline: List[str]
    exe: Optional[str] = None
    cwd: Optional[str] = None
    num_threads: Optional[int] = None
    connections: Optional[List[Dict[str, Any]]] = None


@dataclass
class SystemInfo:
    """System information."""
    
    platform: str
    platform_release: str
    platform_version: str
    architecture: str
    hostname: str
    processor: str
    cpu_count_logical: int
    cpu_count_physical: int
    cpu_freq_current: Optional[float]
    cpu_freq_min: Optional[float]
    cpu_freq_max: Optional[float]
    memory_total: int
    memory_available: int
    memory_percent: float
    swap_total: int
    swap_used: int
    swap_percent: float
    boot_time: datetime
    uptime: float  # seconds since boot


@dataclass
class DiskInfo:
    """Disk/partition information."""
    
    device: str
    mountpoint: str
    fstype: str
    total: int
    used: int
    free: int
    percent: float


@dataclass
class NetworkInfo:
    """Network interface information."""
    
    interface: str
    address: Optional[str] = None
    netmask: Optional[str] = None
    broadcast: Optional[str] = None
    family: Optional[str] = None
    bytes_sent: Optional[int] = None
    bytes_recv: Optional[int] = None
    packets_sent: Optional[int] = None
    packets_recv: Optional[int] = None
    errin: Optional[int] = None
    errout: Optional[int] = None
    dropin: Optional[int] = None
    dropout: Optional[int] = None


@dataclass
class FileInfo:
    """File or directory information."""
    
    path: str
    name: str
    size: int
    is_file: bool
    is_dir: bool
    is_symlink: bool
    permissions: str
    owner: Optional[str]
    group: Optional[str]
    created: datetime
    modified: datetime
    accessed: datetime


@dataclass
class EnvironmentVariable:
    """Environment variable information."""
    
    name: str
    value: str


@dataclass
class ServiceInfo:
    """System service information."""
    
    name: str
    status: str
    description: Optional[str] = None
    pid: Optional[int] = None
    memory_usage: Optional[int] = None


@dataclass
class CommandResult:
    """Result of executing a command."""
    
    command: str
    return_code: int
    stdout: str
    stderr: str
    execution_time: float  # seconds
    success: bool


@dataclass
class PortInfo:
    """Network port information."""
    
    port: int
    protocol: str  # TCP or UDP
    status: str
    pid: Optional[int] = None
    process_name: Optional[str] = None
    local_address: Optional[str] = None
    remote_address: Optional[str] = None


# Type aliases for common data structures
ProcessList = List[ProcessInfo]
DiskList = List[DiskInfo]
NetworkList = List[NetworkInfo]
FileList = List[FileInfo]
PortList = List[PortInfo]
EnvironmentDict = Dict[str, str] 