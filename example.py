"""
Example usage of Common Tool MCP Server.

This script demonstrates how to use the Common Tool MCP Server
with various system tools and operations.
"""

import asyncio
import json
from common_tool_mcp_server import CommonToolMCPServer


async def demonstrate_system_tools():
    """Demonstrate various system tools."""
    print("🔧 Common Tool MCP Server - Demo")
    print("=" * 50)
    
    # Create server instance (for demonstration)
    from common_tool_mcp_server.system_client import SystemToolsClient
    client = SystemToolsClient()
    
    try:
        # System Information
        print("\n📊 System Information:")
        system_info = await client.get_system_info()
        print(f"Platform: {system_info.platform} {system_info.platform_release}")
        print(f"Hostname: {system_info.hostname}")
        print(f"CPU Cores: {system_info.cpu_count_logical} logical, {system_info.cpu_count_physical} physical")
        print(f"Memory: {system_info.memory_total // (1024**3)} GB total, {system_info.memory_available // (1024**3)} GB available")
        
        # Process Information
        print("\n⚙️ Process Information:")
        processes = await client.list_processes(filter_name="python")
        print(f"Found {len(processes)} Python processes:")
        for proc in processes[:3]:  # Show first 3
            print(f"  - PID {proc.pid}: {proc.name} (User: {proc.username})")
        
        # Disk Usage
        print("\n💾 Disk Usage:")
        disks = await client.get_disk_usage()
        for disk in disks:
            used_gb = disk.used // (1024**3)
            total_gb = disk.total // (1024**3)
            print(f"  - {disk.mountpoint}: {used_gb}GB / {total_gb}GB ({disk.percent:.1f}% used)")
        
        # Network Information
        print("\n🌐 Network Interfaces:")
        network_info = await client.get_network_info()
        interfaces = {}
        for info in network_info:
            if info.interface not in interfaces:
                interfaces[info.interface] = []
            interfaces[info.interface].append(info)
        
        for interface, addrs in list(interfaces.items())[:3]:  # Show first 3
            print(f"  - {interface}:")
            for addr in addrs[:2]:  # Show first 2 addresses per interface
                if addr.address:
                    print(f"    Address: {addr.address}")
        
        # Environment Variables
        print("\n🌍 Environment Variables (sample):")
        env_vars = await client.get_environment_variables()
        important_vars = ["PATH", "HOME", "USER", "USERNAME", "PYTHONPATH"]
        for var in env_vars:
            if var.name in important_vars:
                value = var.value[:50] + "..." if len(var.value) > 50 else var.value
                print(f"  - {var.name}: {value}")
        
        # File Operations
        print("\n📁 File Operations Demo:")
        files = await client.list_files(".", include_hidden=False)
        print(f"Found {len(files)} files in current directory:")
        for file_info in files[:5]:  # Show first 5
            size_kb = file_info.size // 1024
            file_type = "DIR" if file_info.is_dir else "FILE"
            print(f"  - {file_type}: {file_info.name} ({size_kb} KB)")
        
        # Listening Ports
        print("\n🔌 Listening Ports (sample):")
        ports = await client.get_listening_ports()
        for port in ports[:5]:  # Show first 5
            process_info = f" ({port.process_name})" if port.process_name else ""
            print(f"  - Port {port.port}/{port.protocol.lower()}{process_info}")
        
        # Command Execution Demo
        print("\n💻 Command Execution Demo:")
        if client.platform == "windows":
            result = await client.execute_command("echo Hello from Windows!")
        else:
            result = await client.execute_command("echo 'Hello from Unix!'")
        
        if result.success:
            print(f"Command output: {result.stdout.strip()}")
        else:
            print(f"Command failed: {result.stderr}")
        
        print("\n✅ Demo completed successfully!")
        
    except Exception as e:
        print(f"❌ Error during demo: {str(e)}")


def main():
    """Main function to run the demo."""
    print("Starting Common Tool MCP Server demonstration...")
    asyncio.run(demonstrate_system_tools())


if __name__ == "__main__":
    main() 