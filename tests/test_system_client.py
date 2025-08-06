"""
Tests for SystemToolsClient.
"""

import asyncio
import os
import tempfile
import pytest
from pathlib import Path

from common_tool_mcp_server.system_client import SystemToolsClient
from common_tool_mcp_server.types import ProcessInfo, SystemInfo, DiskInfo


@pytest.fixture
def client():
    """Create a SystemToolsClient instance for testing."""
    return SystemToolsClient()


@pytest.mark.asyncio
class TestProcessManagement:
    """Test process management functionality."""

    async def test_list_processes(self, client):
        """Test listing processes."""
        processes = await client.list_processes()
        assert isinstance(processes, list)
        assert len(processes) > 0
        
        # Check that we get ProcessInfo objects
        for proc in processes[:5]:  # Check first 5
            assert isinstance(proc, ProcessInfo)
            assert proc.pid > 0
            assert isinstance(proc.name, str)
            assert isinstance(proc.status, str)
            assert isinstance(proc.username, str)

    async def test_list_processes_with_filter(self, client):
        """Test listing processes with name filter."""
        # Look for Python processes (should exist during testing)
        processes = await client.list_processes(filter_name="python")
        assert isinstance(processes, list)
        
        for proc in processes:
            assert "python" in proc.name.lower()

    async def test_list_processes_with_details(self, client):
        """Test listing processes with detailed information."""
        processes = await client.list_processes(include_details=True)
        assert isinstance(processes, list)
        assert len(processes) > 0
        
        # Check that detailed info is included
        for proc in processes[:3]:  # Check first 3
            assert isinstance(proc.cpu_percent, float)
            assert isinstance(proc.memory_percent, float)
            assert isinstance(proc.memory_info_rss, int)
            assert isinstance(proc.memory_info_vms, int)


@pytest.mark.asyncio 
class TestSystemInformation:
    """Test system information functionality."""

    async def test_get_system_info(self, client):
        """Test getting system information."""
        info = await client.get_system_info()
        assert isinstance(info, SystemInfo)
        
        # Check basic fields
        assert isinstance(info.platform, str)
        assert len(info.platform) > 0
        assert isinstance(info.hostname, str)
        assert len(info.hostname) > 0
        assert info.cpu_count_logical > 0
        assert info.memory_total > 0

    async def test_get_disk_usage(self, client):
        """Test getting disk usage information."""
        disks = await client.get_disk_usage()
        assert isinstance(disks, list)
        assert len(disks) > 0
        
        for disk in disks:
            assert isinstance(disk, DiskInfo)
            assert disk.total > 0
            assert disk.used >= 0
            assert disk.free >= 0
            assert 0 <= disk.percent <= 100

    async def test_get_network_info(self, client):
        """Test getting network information."""
        network_info = await client.get_network_info()
        assert isinstance(network_info, list)
        # Network interfaces should exist on any system
        assert len(network_info) > 0

    async def test_get_listening_ports(self, client):
        """Test getting listening ports."""
        ports = await client.get_listening_ports()
        assert isinstance(ports, list)
        # There should be at least some listening ports


@pytest.mark.asyncio
class TestFileOperations:
    """Test file operations functionality."""

    async def test_list_files_current_directory(self, client):
        """Test listing files in current directory."""
        files = await client.list_files(".")
        assert isinstance(files, list)
        assert len(files) > 0

    async def test_list_files_nonexistent_directory(self, client):
        """Test listing files in non-existent directory."""
        with pytest.raises(FileNotFoundError):
            await client.list_files("/nonexistent/directory")

    async def test_read_write_file(self, client):
        """Test reading and writing files."""
        with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.txt') as f:
            test_content = "Hello, World!\nThis is a test file."
            f.write(test_content)
            temp_file = f.name

        try:
            # Test reading
            content = await client.read_file(temp_file)
            assert content == test_content

            # Test writing
            new_content = "New content for testing"
            result = await client.write_file(temp_file, new_content)
            assert result.success
            assert result.return_code == 0

            # Verify the write
            written_content = await client.read_file(temp_file)
            assert written_content == new_content

            # Test appending
            append_content = "\nAppended content"
            result = await client.write_file(temp_file, append_content, append=True)
            assert result.success

            # Verify the append
            final_content = await client.read_file(temp_file)
            assert final_content == new_content + append_content

        finally:
            # Clean up
            os.unlink(temp_file)

    async def test_read_nonexistent_file(self, client):
        """Test reading non-existent file."""
        with pytest.raises(FileNotFoundError):
            await client.read_file("/nonexistent/file.txt")


@pytest.mark.asyncio
class TestCommandExecution:
    """Test command execution functionality."""

    async def test_execute_simple_command(self, client):
        """Test executing a simple command."""
        # Use platform-appropriate command
        if client.platform == "windows":
            command = "echo Hello World"
        else:
            command = "echo 'Hello World'"
        
        result = await client.execute_command(command)
        assert result.success
        assert result.return_code == 0
        assert "Hello World" in result.stdout

    async def test_execute_command_with_timeout(self, client):
        """Test command execution with timeout."""
        # Use platform-appropriate sleep command
        if client.platform == "windows":
            command = "timeout 2"  # Windows timeout command
        else:
            command = "sleep 2"
        
        result = await client.execute_command(command, timeout=1.0)
        assert not result.success
        assert result.return_code == 124  # timeout exit code

    async def test_execute_failing_command(self, client):
        """Test executing a command that fails."""
        command = "nonexistent_command_12345"
        result = await client.execute_command(command)
        assert not result.success
        assert result.return_code != 0


@pytest.mark.asyncio
class TestEnvironmentVariables:
    """Test environment variable functionality."""

    async def test_get_environment_variables(self, client):
        """Test getting all environment variables."""
        env_vars = await client.get_environment_variables()
        assert isinstance(env_vars, list)
        assert len(env_vars) > 0
        
        # Check that PATH exists (should exist on all systems)
        path_vars = [var for var in env_vars if var.name == "PATH"]
        assert len(path_vars) > 0

    async def test_get_specific_environment_variable(self, client):
        """Test getting a specific environment variable."""
        # PATH should exist on all systems
        path_value = await client.get_environment_variable("PATH")
        assert path_value is not None
        assert isinstance(path_value, str)
        assert len(path_value) > 0

    async def test_get_nonexistent_environment_variable(self, client):
        """Test getting a non-existent environment variable."""
        value = await client.get_environment_variable("NONEXISTENT_VAR_12345")
        assert value is None

    async def test_set_environment_variable(self, client):
        """Test setting an environment variable."""
        test_name = "TEST_VAR_12345"
        test_value = "test_value"
        
        # Set the variable
        result = await client.set_environment_variable(test_name, test_value)
        assert result.success
        assert result.return_code == 0
        
        # Verify it was set
        retrieved_value = await client.get_environment_variable(test_name)
        assert retrieved_value == test_value


@pytest.mark.asyncio
class TestNetworkTools:
    """Test network tools functionality."""

    async def test_ping_localhost(self, client):
        """Test pinging localhost."""
        result = await client.ping_host("localhost", count=1)
        # Note: This might fail in some CI environments, so we don't assert success
        assert isinstance(result.stdout, str)
        assert isinstance(result.stderr, str)
        assert isinstance(result.return_code, int) 