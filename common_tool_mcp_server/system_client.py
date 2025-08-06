"""
System tools client for executing common system commands and operations.
"""

import asyncio
import os
import platform
import shutil
import signal
import subprocess
import time
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, List, Optional, Union, Any
import psutil
import aiofiles

from .types import (
    ProcessInfo,
    SystemInfo,
    DiskInfo,
    NetworkInfo,
    FileInfo,
    CommandResult,
    PortInfo,
    EnvironmentVariable,
    ProcessList,
    DiskList,
    NetworkList,
    FileList,
    PortList,
)


class SystemToolsClient:
    """Client for executing system tools and commands."""

    def __init__(self) -> None:
        """Initialize the system tools client."""
        self.platform = platform.system().lower()

    # Process Management
    async def list_processes(
        self, 
        filter_name: Optional[str] = None,
        filter_user: Optional[str] = None,
        include_details: bool = False
    ) -> ProcessList:
        """List running processes with optional filtering."""
        processes = []
        
        for proc in psutil.process_iter(['pid', 'name', 'username', 'status', 'create_time']):
            try:
                pinfo = proc.info
                
                # Apply filters
                if filter_name and filter_name.lower() not in pinfo['name'].lower():
                    continue
                if filter_user and pinfo['username'] != filter_user:
                    continue
                
                # Get basic info
                process_info = ProcessInfo(
                    pid=pinfo['pid'],
                    name=pinfo['name'],
                    status=pinfo['status'],
                    username=pinfo['username'] or 'Unknown',
                    cpu_percent=0.0,
                    memory_percent=0.0,
                    memory_info_rss=0,
                    memory_info_vms=0,
                    create_time=datetime.fromtimestamp(pinfo['create_time'], tz=timezone.utc),
                    cmdline=[]
                )
                
                # Get detailed info if requested
                if include_details:
                    try:
                        process_info.cpu_percent = proc.cpu_percent()
                        memory_info = proc.memory_info()
                        process_info.memory_info_rss = memory_info.rss
                        process_info.memory_info_vms = memory_info.vms
                        process_info.memory_percent = proc.memory_percent()
                        process_info.cmdline = proc.cmdline()
                        process_info.exe = proc.exe()
                        process_info.cwd = proc.cwd()
                        process_info.num_threads = proc.num_threads()
                    except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
                        pass
                
                processes.append(process_info)
                
            except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
                continue
        
        return processes

    async def kill_process(self, pid: int, force: bool = False) -> CommandResult:
        """Kill a process by PID."""
        start_time = time.time()
        
        try:
            proc = psutil.Process(pid)
            process_name = proc.name()
            
            if force:
                proc.kill()  # SIGKILL
                action = "force killed"
            else:
                proc.terminate()  # SIGTERM
                action = "terminated"
            
            # Wait for process to end
            try:
                proc.wait(timeout=5)
            except psutil.TimeoutExpired:
                if not force:
                    proc.kill()
                    action = "force killed after timeout"
            
            execution_time = time.time() - start_time
            return CommandResult(
                command=f"kill {'--force' if force else ''} {pid}",
                return_code=0,
                stdout=f"Process {process_name} (PID: {pid}) {action} successfully",
                stderr="",
                execution_time=execution_time,
                success=True
            )
            
        except psutil.NoSuchProcess:
            execution_time = time.time() - start_time
            return CommandResult(
                command=f"kill {'--force' if force else ''} {pid}",
                return_code=1,
                stdout="",
                stderr=f"Process with PID {pid} not found",
                execution_time=execution_time,
                success=False
            )
        except psutil.AccessDenied:
            execution_time = time.time() - start_time
            return CommandResult(
                command=f"kill {'--force' if force else ''} {pid}",
                return_code=1,
                stdout="",
                stderr=f"Access denied to kill process {pid}",
                execution_time=execution_time,
                success=False
            )
        except Exception as e:
            execution_time = time.time() - start_time
            return CommandResult(
                command=f"kill {'--force' if force else ''} {pid}",
                return_code=1,
                stdout="",
                stderr=f"Error killing process {pid}: {str(e)}",
                execution_time=execution_time,
                success=False
            )

    async def kill_processes_by_name(self, name: str, force: bool = False) -> CommandResult:
        """Kill all processes with the given name."""
        start_time = time.time()
        killed_pids = []
        errors = []
        
        for proc in psutil.process_iter(['pid', 'name']):
            try:
                if proc.info['name'].lower() == name.lower():
                    pid = proc.info['pid']
                    if force:
                        proc.kill()
                    else:
                        proc.terminate()
                    killed_pids.append(pid)
            except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess) as e:
                errors.append(f"PID {proc.info['pid']}: {str(e)}")
        
        execution_time = time.time() - start_time
        
        if killed_pids:
            return CommandResult(
                command=f"killall {'--force' if force else ''} {name}",
                return_code=0,
                stdout=f"Killed processes: {killed_pids}",
                stderr="\n".join(errors) if errors else "",
                execution_time=execution_time,
                success=True
            )
        else:
            return CommandResult(
                command=f"killall {'--force' if force else ''} {name}",
                return_code=1,
                stdout="",
                stderr=f"No processes found with name '{name}'",
                execution_time=execution_time,
                success=False
            )

    # System Information
    async def get_system_info(self) -> SystemInfo:
        """Get comprehensive system information."""
        cpu_freq = psutil.cpu_freq()
        memory = psutil.virtual_memory()
        swap = psutil.swap_memory()
        boot_time = psutil.boot_time()
        
        return SystemInfo(
            platform=platform.system(),
            platform_release=platform.release(),
            platform_version=platform.version(),
            architecture=platform.machine(),
            hostname=platform.node(),
            processor=platform.processor(),
            cpu_count_logical=psutil.cpu_count(logical=True),
            cpu_count_physical=psutil.cpu_count(logical=False),
            cpu_freq_current=cpu_freq.current if cpu_freq else None,
            cpu_freq_min=cpu_freq.min if cpu_freq else None,
            cpu_freq_max=cpu_freq.max if cpu_freq else None,
            memory_total=memory.total,
            memory_available=memory.available,
            memory_percent=memory.percent,
            swap_total=swap.total,
            swap_used=swap.used,
            swap_percent=swap.percent,
            boot_time=datetime.fromtimestamp(boot_time, tz=timezone.utc),
            uptime=time.time() - boot_time,
        )

    async def get_disk_usage(self, path: str = "/") -> DiskList:
        """Get disk usage information for all mounted disks or a specific path."""
        disks = []
        
        if path != "/":
            # Get usage for specific path
            try:
                usage = shutil.disk_usage(path)
                disks.append(DiskInfo(
                    device=path,
                    mountpoint=path,
                    fstype="unknown",
                    total=usage.total,
                    used=usage.used,
                    free=usage.free,
                    percent=(usage.used / usage.total) * 100 if usage.total > 0 else 0
                ))
            except Exception as e:
                raise Exception(f"Error getting disk usage for {path}: {str(e)}")
        else:
            # Get usage for all mounted disks
            for partition in psutil.disk_partitions():
                try:
                    usage = psutil.disk_usage(partition.mountpoint)
                    disks.append(DiskInfo(
                        device=partition.device,
                        mountpoint=partition.mountpoint,
                        fstype=partition.fstype,
                        total=usage.total,
                        used=usage.used,
                        free=usage.free,
                        percent=usage.percent
                    ))
                except (PermissionError, FileNotFoundError):
                    continue
        
        return disks

    async def get_network_info(self) -> NetworkList:
        """Get network interface information."""
        interfaces = []
        
        # Get interface addresses
        addresses = psutil.net_if_addrs()
        stats = psutil.net_if_stats()
        io_counters = psutil.net_io_counters(pernic=True)
        
        for interface_name, addr_list in addresses.items():
            for addr in addr_list:
                net_info = NetworkInfo(
                    interface=interface_name,
                    address=addr.address,
                    netmask=addr.netmask,
                    broadcast=addr.broadcast,
                    family=str(addr.family)
                )
                
                # Add IO statistics if available
                if interface_name in io_counters:
                    io = io_counters[interface_name]
                    net_info.bytes_sent = io.bytes_sent
                    net_info.bytes_recv = io.bytes_recv
                    net_info.packets_sent = io.packets_sent
                    net_info.packets_recv = io.packets_recv
                    net_info.errin = io.errin
                    net_info.errout = io.errout
                    net_info.dropin = io.dropin
                    net_info.dropout = io.dropout
                
                interfaces.append(net_info)
        
        return interfaces

    # File Operations
    async def list_files(
        self, 
        directory: str = ".", 
        include_hidden: bool = False,
        recursive: bool = False
    ) -> FileList:
        """List files and directories."""
        files = []
        path = Path(directory)
        
        if not path.exists():
            raise FileNotFoundError(f"Directory '{directory}' not found")
        
        if not path.is_dir():
            raise NotADirectoryError(f"'{directory}' is not a directory")
        
        def process_path(p: Path) -> FileInfo:
            stat = p.stat()
            return FileInfo(
                path=str(p),
                name=p.name,
                size=stat.st_size,
                is_file=p.is_file(),
                is_dir=p.is_dir(),
                is_symlink=p.is_symlink(),
                permissions=oct(stat.st_mode)[-3:],
                owner=None,  # Would need pwd module for Unix systems
                group=None,  # Would need grp module for Unix systems  
                created=datetime.fromtimestamp(stat.st_ctime, tz=timezone.utc),
                modified=datetime.fromtimestamp(stat.st_mtime, tz=timezone.utc),
                accessed=datetime.fromtimestamp(stat.st_atime, tz=timezone.utc),
            )
        
        try:
            if recursive:
                for item in path.rglob("*"):
                    if not include_hidden and item.name.startswith('.'):
                        continue
                    files.append(process_path(item))
            else:
                for item in path.iterdir():
                    if not include_hidden and item.name.startswith('.'):
                        continue
                    files.append(process_path(item))
        except PermissionError as e:
            raise PermissionError(f"Permission denied accessing '{directory}': {str(e)}")
        
        return files

    async def read_file(self, filepath: str, encoding: str = "utf-8") -> str:
        """Read file contents."""
        try:
            async with aiofiles.open(filepath, 'r', encoding=encoding) as f:
                return await f.read()
        except FileNotFoundError:
            raise FileNotFoundError(f"File '{filepath}' not found")
        except PermissionError:
            raise PermissionError(f"Permission denied reading file '{filepath}'")
        except UnicodeDecodeError as e:
            raise UnicodeDecodeError(
                e.encoding, e.object, e.start, e.end,
                f"Unable to decode file '{filepath}' with encoding '{encoding}'"
            )

    async def write_file(
        self, 
        filepath: str, 
        content: str, 
        encoding: str = "utf-8",
        append: bool = False
    ) -> CommandResult:
        """Write content to a file."""
        start_time = time.time()
        
        try:
            mode = 'a' if append else 'w'
            async with aiofiles.open(filepath, mode, encoding=encoding) as f:
                await f.write(content)
            
            execution_time = time.time() - start_time
            action = "appended to" if append else "written to"
            
            return CommandResult(
                command=f"write {'--append' if append else ''} {filepath}",
                return_code=0,
                stdout=f"Content {action} '{filepath}' successfully",
                stderr="",
                execution_time=execution_time,
                success=True
            )
        except Exception as e:
            execution_time = time.time() - start_time
            return CommandResult(
                command=f"write {'--append' if append else ''} {filepath}",
                return_code=1,
                stdout="",
                stderr=f"Error writing to file '{filepath}': {str(e)}",
                execution_time=execution_time,
                success=False
            )

    # Command Execution
    async def execute_command(
        self, 
        command: str, 
        cwd: Optional[str] = None,
        timeout: Optional[float] = None,
        shell: bool = True
    ) -> CommandResult:
        """Execute a shell command."""
        start_time = time.time()
        
        try:
            process = await asyncio.create_subprocess_shell(
                command,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE,
                cwd=cwd
            ) if shell else await asyncio.create_subprocess_exec(
                *command.split(),
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE,
                cwd=cwd
            )
            
            stdout, stderr = await asyncio.wait_for(
                process.communicate(), 
                timeout=timeout
            )
            
            execution_time = time.time() - start_time
            
            return CommandResult(
                command=command,
                return_code=process.returncode or 0,
                stdout=stdout.decode('utf-8', errors='replace'),
                stderr=stderr.decode('utf-8', errors='replace'),
                execution_time=execution_time,
                success=process.returncode == 0
            )
            
        except asyncio.TimeoutError:
            execution_time = time.time() - start_time
            return CommandResult(
                command=command,
                return_code=124,  # timeout exit code
                stdout="",
                stderr=f"Command timed out after {timeout} seconds",
                execution_time=execution_time,
                success=False
            )
        except Exception as e:
            execution_time = time.time() - start_time
            return CommandResult(
                command=command,
                return_code=1,
                stdout="",
                stderr=f"Error executing command: {str(e)}",
                execution_time=execution_time,
                success=False
            )

    # Network Tools
    async def get_listening_ports(self) -> PortList:
        """Get list of listening network ports."""
        ports = []
        
        for conn in psutil.net_connections(kind='inet'):
            if conn.status == psutil.CONN_LISTEN:
                try:
                    process = psutil.Process(conn.pid) if conn.pid else None
                    process_name = process.name() if process else None
                except (psutil.NoSuchProcess, psutil.AccessDenied):
                    process_name = None
                
                port_info = PortInfo(
                    port=conn.laddr.port,
                    protocol=conn.type.name if hasattr(conn.type, 'name') else str(conn.type),
                    status=conn.status,
                    pid=conn.pid,
                    process_name=process_name,
                    local_address=conn.laddr.ip if conn.laddr else None,
                    remote_address=f"{conn.raddr.ip}:{conn.raddr.port}" if conn.raddr else None
                )
                
                ports.append(port_info)
        
        return ports

    async def ping_host(self, host: str, count: int = 4) -> CommandResult:
        """Ping a host."""
        if self.platform == "windows":
            command = f"ping -n {count} {host}"
        else:
            command = f"ping -c {count} {host}"
        
        return await self.execute_command(command)

    # Environment Variables
    async def get_environment_variables(self) -> List[EnvironmentVariable]:
        """Get all environment variables."""
        return [
            EnvironmentVariable(name=name, value=value)
            for name, value in os.environ.items()
        ]

    async def get_environment_variable(self, name: str) -> Optional[str]:
        """Get a specific environment variable."""
        return os.environ.get(name)

    async def set_environment_variable(self, name: str, value: str) -> CommandResult:
        """Set an environment variable (for current session only)."""
        start_time = time.time()
        
        try:
            os.environ[name] = value
            execution_time = time.time() - start_time
            
            return CommandResult(
                command=f"export {name}={value}",
                return_code=0,
                stdout=f"Environment variable '{name}' set to '{value}'",
                stderr="",
                execution_time=execution_time,
                success=True
            )
        except Exception as e:
            execution_time = time.time() - start_time
            return CommandResult(
                command=f"export {name}={value}",
                return_code=1,
                stdout="",
                stderr=f"Error setting environment variable: {str(e)}",
                execution_time=execution_time,
                success=False
            ) 