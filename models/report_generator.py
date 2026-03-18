import json
import datetime

class ReportGenerator:
    """
    Zero-Dependency System Report Engine.
    Compiles raw and cached system metrics into human-readable (.txt) or machine-readable (.json) formats.
    """
    @staticmethod
    def generate_json(data_snapshot, filepath):
        """Writes a raw JSON dictionary to disk."""
        try:
            with open(filepath, 'w') as f:
                json.dump(data_snapshot, f, indent=4)
            return True, "JSON Report exported successfully."
        except Exception as e:
            return False, f"Failed to export JSON: {str(e)}"

    @staticmethod
    def generate_txt(data_snapshot, filepath):
        """Formats the data snapshot into a clean, human-readable ASCII/Markdown report."""
        try:
            timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            lines = []

            lines.append("==================================================")
            lines.append("                4n4lyz3r SYSTEM REPORT            ")
            lines.append("==================================================")
            lines.append(f"Generated On: {timestamp}")
            lines.append("")

            # OS & Hardware Base
            lines.append("[ SYSTEM & DEEP SPECS ]")
            ds = data_snapshot.get("deep_specs", {})
            lines.append(f"- OS Platform: {data_snapshot.get('os_platform', 'Unknown')}")
            lines.append(f"- BIOS: {ds.get('bios', 'N/A')}")
            lines.append(f"- Motherboard: {ds.get('motherboard', 'N/A')}")
            lines.append("")

            # Active Hardware Performance
            lines.append("[ CURRENT HARDWARE PERFORMANCE ]")
            lines.append(f"- CPU Usage: {data_snapshot.get('cpu', 'N/A')}%")

            ram = data_snapshot.get("ram", {})
            if isinstance(ram, dict):
                lines.append(f"- RAM Usage: {ram.get('percent', 'N/A')}% ({ram.get('used_gb', 'N/A')} GB / {ram.get('total_gb', 'N/A')} GB)")

            disk = data_snapshot.get("disk", {})
            if isinstance(disk, dict):
                lines.append(f"- Disk Usage: {disk.get('percent', 'N/A')}% ({disk.get('used_gb', 'N/A')} GB / {disk.get('total_gb', 'N/A')} GB)")
                lines.append(f"- Disk I/O Speeds: R: {disk.get('read_speed_mb', 'N/A')} MB/s | W: {disk.get('write_speed_mb', 'N/A')} MB/s")

            net = data_snapshot.get("network", {})
            if isinstance(net, dict):
                lines.append(f"- Network Speeds: DL: {net.get('down_speed_mb', 'N/A')} MB/s | UL: {net.get('up_speed_mb', 'N/A')} MB/s")

            gpu = data_snapshot.get("gpu", {})
            if isinstance(gpu, dict):
                lines.append(f"- GPU Usage: {gpu.get('percent', 'N/A')}% (VRAM: {gpu.get('memory_used', 'N/A')} MB / {gpu.get('memory_total', 'N/A')} MB)")
            lines.append("")

            # Battery & Deep Health
            lines.append("[ HARDWARE HEALTH ANALYTICS ]")
            bat = ds.get("battery_health", {})
            lines.append(f"- Battery Status: {bat.get('status', 'N/A')}")
            if bat.get('status') == 'Found':
                lines.append(f"  > Wear Level: {bat.get('wear_level', 'N/A')}%")
                lines.append(f"  > Charge Capacity: {bat.get('health_pct', 'N/A')}%")
                lines.append(f"  > Grade: {bat.get('grade', 'N/A')}")

            lines.append("- S.M.A.R.T Disk Diagnostics:")
            disks = ds.get("smart_disks", [])
            if disks:
                for d in disks:
                    lines.append(f"  > Drive: {d.get('model', 'Unknown')} | Status: {d.get('status', 'Unknown')} | Grade: {d.get('grade', 'Unknown')}")
            else:
                lines.append("  > No S.M.A.R.T data available.")
            lines.append("")

            # Threat Heuristics
            lines.append("[ ACTIVE THREAT HEURISTICS (TOP PROCESSES) ]")
            procs = data_snapshot.get("top_processes", [])
            if procs:
                for p in procs:
                    susp = "[SUSPICIOUS]" if p.get('suspicious', False) else ""
                    lines.append(f"- PID: {p.get('pid', 'N/A')} | {p.get('name', 'Unknown')[:15].ljust(15)} | CPU: {p.get('cpu_percent', 0):.1f}% | RAM: {p.get('memory_percent', 0):.1f}% {susp}")
            else:
                lines.append("- No top processes tracked.")
            lines.append("")

            # Network Connections
            lines.append("[ ACTIVE NETWORK CONNECTIONS ]")
            conns = data_snapshot.get("net_connections", [])
            if conns:
                for c in conns:
                    lines.append(f"- [{c.get('type', '???')}] {c.get('local', 'N/A')} => {c.get('remote', 'N/A')} | {c.get('status', 'N/A')} | PID: {c.get('pid', 'N/A')}")
            else:
                lines.append("- No active network connections available.")

            lines.append("==================================================")
            lines.append("                 END OF REPORT                    ")
            lines.append("==================================================")

            with open(filepath, 'w', encoding='utf-8') as f:
                f.write("\n".join(lines))

            return True, "TXT Report exported successfully."
        except Exception as e:
            return False, f"Failed to export TXT: {str(e)}"
