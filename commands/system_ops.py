"""
System monitoring operations using psutil.
"""
import psutil
from typing import List


def cpu_command(args: List[str]) -> str:
    """
    Display CPU usage information.

    Args:
        args (List[str]): Command arguments

    Returns:
        str: Formatted CPU usage information
    """
    try:
        # Get CPU usage
        cpu_percent = psutil.cpu_percent(interval=1)
        cpu_count = psutil.cpu_count()
        cpu_freq = psutil.cpu_freq()

        # Get per-CPU usage
        per_cpu = psutil.cpu_percent(interval=1, percpu=True)

        # Get load average (Unix-like systems)
        try:
            load_avg = psutil.getloadavg()
            load_info = f"Load Average: {load_avg[0]:.2f}, {load_avg[1]:.2f}, {load_avg[2]:.2f}"
        except AttributeError:
            load_info = "Load Average: Not available on this system"

        # Format output
        output = []
        output.append("=== CPU Information ===")
        output.append(f"CPU Cores: {cpu_count}")
        output.append(f"Overall CPU Usage: {cpu_percent}%")

        if cpu_freq:
            output.append(f"Current Frequency: {cpu_freq.current:.2f} MHz")
            output.append(f"Min Frequency: {cpu_freq.min:.2f} MHz")
            output.append(f"Max Frequency: {cpu_freq.max:.2f} MHz")

        output.append(load_info)
        output.append("")

        # Per-CPU usage
        output.append("Per-CPU Usage:")
        for i, usage in enumerate(per_cpu):
            output.append(f"  CPU {i}: {usage:6.1f}%")

        return "\n".join(output)

    except Exception as e:
        return f"Error getting CPU information: {str(e)}"


def mem_command(args: List[str]) -> str:
    """
    Display memory usage information.

    Args:
        args (List[str]): Command arguments

    Returns:
        str: Formatted memory usage information
    """
    try:
        # Get memory information
        memory = psutil.virtual_memory()
        swap = psutil.swap_memory()

        # Format memory sizes
        def format_bytes(bytes_value):
            for unit in ['B', 'KB', 'MB', 'GB', 'TB']:
                if bytes_value < 1024.0:
                    return f"{bytes_value:.1f} {unit}"
                bytes_value /= 1024.0
            return f"{bytes_value:.1f} PB"

        # Calculate percentages
        memory_used_percent = memory.percent
        swap_used_percent = swap.percent if swap.total > 0 else 0

        # Format output
        output = []
        output.append("=== Memory Information ===")
        output.append("Virtual Memory:")
        output.append(f"  Total: {format_bytes(memory.total)}")
        output.append(f"  Available: {format_bytes(memory.available)}")
        output.append(
            f"  Used: {format_bytes(memory.used)} ({memory_used_percent:.1f}%)")
        output.append(f"  Free: {format_bytes(memory.free)}")
        output.append("")

        output.append("Swap Memory:")
        if swap.total > 0:
            output.append(f"  Total: {format_bytes(swap.total)}")
            output.append(
                f"  Used: {format_bytes(swap.used)} ({swap_used_percent:.1f}%)")
            output.append(f"  Free: {format_bytes(swap.free)}")
        else:
            output.append("  No swap memory configured")

        # Memory usage bar
        output.append("")
        output.append("Memory Usage Bar:")
        bar_length = 50
        used_bars = int((memory_used_percent / 100) * bar_length)
        free_bars = bar_length - used_bars
        bar = "█" * used_bars + "░" * free_bars
        output.append(f"  [{bar}] {memory_used_percent:.1f}%")

        return "\n".join(output)

    except Exception as e:
        return f"Error getting memory information: {str(e)}"


def ps_command(args: List[str]) -> str:
    """
    Display running processes.

    Args:
        args (List[str]): Command arguments

    Returns:
        str: Formatted process list
    """
    try:
        # Parse arguments
        show_all = False
        max_processes = 20  # Default limit

        for arg in args:
            if arg == '-a' or arg == '--all':
                show_all = True
            elif arg.isdigit():
                max_processes = int(arg)

        # Get all processes
        processes = []
        for proc in psutil.process_iter(['pid', 'name', 'cpu_percent', 'memory_percent', 'status']):
            try:
                proc_info = proc.info
                processes.append(proc_info)
            except (psutil.NoSuchProcess, psutil.AccessDenied):
                continue

        # Sort by CPU usage (descending)
        processes.sort(key=lambda x: x['cpu_percent'] or 0, reverse=True)

        # Limit number of processes
        if not show_all:
            processes = processes[:max_processes]

        # Format output
        output = []
        output.append("=== Running Processes ===")
        output.append(
            f"{'PID':<8} {'Name':<20} {'CPU%':<8} {'Memory%':<10} {'Status':<12}")
        output.append("-" * 70)

        for proc in processes:
            pid = str(proc['pid'])
            name = proc['name'][:19]  # Truncate long names
            cpu_percent = f"{proc['cpu_percent']:.1f}" if proc['cpu_percent'] is not None else "0.0"
            memory_percent = f"{proc['memory_percent']:.1f}" if proc['memory_percent'] is not None else "0.0"
            status = proc['status'][:11]  # Truncate long status

            output.append(
                f"{pid:<8} {name:<20} {cpu_percent:<8} {memory_percent:<10} {status:<12}")

        if not show_all and len(processes) == max_processes:
            output.append(
                f"\n... showing top {max_processes} processes by CPU usage")
            output.append("Use 'ps -a' to show all processes")

        return "\n".join(output)

    except Exception as e:
        return f"Error getting process information: {str(e)}"


def disk_command(args: List[str]) -> str:
    """
    Display disk usage information.

    Args:
        args (List[str]): Command arguments

    Returns:
        str: Formatted disk usage information
    """
    try:
        # Get disk usage
        disk_usage = psutil.disk_usage('/')
        disk_io = psutil.disk_io_counters()

        # Format sizes
        def format_bytes(bytes_value):
            for unit in ['B', 'KB', 'MB', 'GB', 'TB']:
                if bytes_value < 1024.0:
                    return f"{bytes_value:.1f} {unit}"
                bytes_value /= 1024.0
            return f"{bytes_value:.1f} PB"

        # Calculate percentages
        used_percent = (disk_usage.used / disk_usage.total) * 100
        free_percent = (disk_usage.free / disk_usage.total) * 100

        # Format output
        output = []
        output.append("=== Disk Usage ===")
        output.append(f"Total Space: {format_bytes(disk_usage.total)}")
        output.append(
            f"Used Space: {format_bytes(disk_usage.used)} ({used_percent:.1f}%)")
        output.append(
            f"Free Space: {format_bytes(disk_usage.free)} ({free_percent:.1f}%)")

        # Disk usage bar
        output.append("")
        output.append("Disk Usage Bar:")
        bar_length = 50
        used_bars = int((used_percent / 100) * bar_length)
        free_bars = bar_length - used_bars
        bar = "█" * used_bars + "░" * free_bars
        output.append(f"[{bar}] {used_percent:.1f}%")

        if disk_io:
            output.append("")
            output.append("Disk I/O:")
            output.append(
                f"  Reads: {disk_io.read_count} ({format_bytes(disk_io.read_bytes)})")
            output.append(
                f"  Writes: {disk_io.write_count} ({format_bytes(disk_io.write_bytes)})")

        return "\n".join(output)

    except Exception as e:
        return f"Error getting disk information: {str(e)}"
