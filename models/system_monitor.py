import psutil
import platform
import time
import collections
import ipaddress
import subprocess
try:
    import GPUtil
    _HAS_GPUTIL = True
except ImportError:
    _HAS_GPUTIL = False

import threading
from models.native_os import NativePoller
from models.health_analyzer import HardwareHealthAnalyzer

# Constants for Active Threat Heuristics
SUSPICIOUS_PATHS = [
    "/tmp", "/var/tmp", "/dev/shm",
    "AppData\\Local\\Temp", "AppData\\Roaming",
    "C:\\Windows\\Temp", "AppData\\LocalLow", "Downloads"
]

class Model_4n4lyz3r:
    """
    Model class to fetch and process system metrics for 4n4lyz3r.
    Handles fallbacks for OS-specific restrictions gracefully.
    Implements extreme static caching, memory leak prevention, and native C-level bypassing.
    """

    def __init__(self):
        self.os_platform = platform.system()
        self.native_poller = NativePoller()
        self.health_analyzer = HardwareHealthAnalyzer()

        # Initialize psutil counters to avoid blocking/spikes on first fetch
        psutil.cpu_percent()
        self.native_poller.get_cpu_percent_native() # Prime native poller

        # --- EXTREME CACHING (Static Specs) ---
        self.cached_specs = {
            "battery_health": {"status": "Fetching...", "wear_level": 0.0, "grade": ""},
            "smart_disks": []
        }

        # Spawn an async daemon thread to fetch heavy deep health analytics so we don't block startup
        threading.Thread(target=self._fetch_deep_health_analytics_daemon, daemon=True).start()

        # Cache RAM total
        try:
            mem = psutil.virtual_memory()
            self.cached_specs["ram_total_gb"] = round(mem.total / (1024 ** 3), 2)
        except Exception:
            self.cached_specs["ram_total_gb"] = "N/A"

        # Cache Disk total
        try:
            path = '/' if self.os_platform != 'Windows' else 'C:\\'
            disk = psutil.disk_usage(path)
            self.cached_specs["disk_total_gb"] = round(disk.total / (1024 ** 3), 2)
        except Exception:
            self.cached_specs["disk_total_gb"] = "N/A"

        # --- DYNAMIC DATA & MEMORY LEAK PREVENTION ---
        # Historical arrays bounded by deque(maxlen)
        self.history_cpu = collections.deque(maxlen=60)
        self.history_ram = collections.deque(maxlen=60)

        # Disk IO state
        self.last_disk_io = psutil.disk_io_counters()
        self.last_disk_time = time.time()

        # Network IO state
        self.last_net_io = psutil.net_io_counters()
        self.last_net_time = time.time()

        # GPU State
        self.has_gpu = _HAS_GPUTIL
        if self.has_gpu:
            try:
                gpus = GPUtil.getGPUs()
                if not gpus:
                    self.has_gpu = False
                else:
                    self.cached_specs["gpu_total_mb"] = round(gpus[0].memoryTotal, 1)
            except Exception:
                self.has_gpu = False

    def _fetch_deep_health_analytics_daemon(self):
        """Asynchronously fetches deep hardware wear/tear and caches it."""
        try:
            bat_health = self.health_analyzer.analyze_battery()
            disk_health = self.health_analyzer.analyze_disks()

            self.cached_specs["battery_health"] = bat_health
            self.cached_specs["smart_disks"] = disk_health
        except Exception:
            pass

    def get_cpu_metrics(self):
        """Returns CPU usage percentage via native OS hooks (if supported) and pushes to bounded history."""
        try:
            val = self.native_poller.get_cpu_percent_native()
            if val is None:
                # Fallback to psutil if native hook failed or is unsupported
                val = psutil.cpu_percent(interval=None)
            self.history_cpu.append(val)
            return val
        except Exception:
            return "N/A"

    def get_ram_metrics(self):
        """Returns RAM usage percentage and pushes to bounded history."""
        try:
            mem = psutil.virtual_memory()
            used_gb = mem.used / (1024 ** 3)
            self.history_ram.append(mem.percent)
            return {
                "percent": mem.percent,
                "used_gb": round(used_gb, 2),
                "total_gb": self.cached_specs.get("ram_total_gb", "N/A")
            }
        except Exception:
            return {"percent": "N/A", "used_gb": "N/A", "total_gb": self.cached_specs.get("ram_total_gb", "N/A")}

    def get_disk_metrics(self):
        """Returns Disk usage percentage and total/used space for the main partition, plus read/write speeds."""
        try:
            # Check the root partition ('/' on Linux/Mac, 'C:\\' on Windows)
            path = '/' if self.os_platform != 'Windows' else 'C:\\'
            disk = psutil.disk_usage(path)
            used_gb = disk.used / (1024 ** 3)

            # Calculate speeds
            current_time = time.time()
            current_io = psutil.disk_io_counters()
            time_diff = current_time - self.last_disk_time

            read_speed_mb = 0
            write_speed_mb = 0

            if time_diff > 0 and current_io and self.last_disk_io:
                read_bytes = current_io.read_bytes - self.last_disk_io.read_bytes
                write_bytes = current_io.write_bytes - self.last_disk_io.write_bytes

                # MB/s
                read_speed_mb = (read_bytes / (1024 * 1024)) / time_diff
                write_speed_mb = (write_bytes / (1024 * 1024)) / time_diff

            self.last_disk_io = current_io
            self.last_disk_time = current_time

            return {
                "percent": disk.percent,
                "used_gb": round(used_gb, 2),
                "total_gb": self.cached_specs.get("disk_total_gb", "N/A"),
                "read_speed_mb": round(read_speed_mb, 2),
                "write_speed_mb": round(write_speed_mb, 2)
            }
        except Exception:
            return {
                "percent": "N/A", "used_gb": "N/A",
                "total_gb": self.cached_specs.get("disk_total_gb", "N/A"),
                "read_speed_mb": "N/A", "write_speed_mb": "N/A"
            }

    def get_network_metrics(self):
        """Returns network upload/download speeds in MB/s."""
        try:
            current_time = time.time()
            current_io = psutil.net_io_counters()
            time_diff = current_time - self.last_net_time

            up_speed_mb = 0
            down_speed_mb = 0

            if time_diff > 0 and current_io and self.last_net_io:
                up_bytes = current_io.bytes_sent - self.last_net_io.bytes_sent
                down_bytes = current_io.bytes_recv - self.last_net_io.bytes_recv

                up_speed_mb = (up_bytes / (1024 * 1024)) / time_diff
                down_speed_mb = (down_bytes / (1024 * 1024)) / time_diff

            self.last_net_io = current_io
            self.last_net_time = current_time

            return {
                "up_speed_mb": round(up_speed_mb, 2),
                "down_speed_mb": round(down_speed_mb, 2)
            }
        except Exception:
            return {"up_speed_mb": "N/A", "down_speed_mb": "N/A"}

    def get_gpu_metrics(self):
        """Returns GPU usage and VRAM stats if available."""
        if not self.has_gpu:
            return {"percent": "N/A", "memory_used": "N/A", "memory_total": "N/A"}

        try:
            gpus = GPUtil.getGPUs()
            if gpus:
                gpu = gpus[0]
                return {
                    "percent": round(gpu.load * 100, 1),
                    "memory_used": round(gpu.memoryUsed, 1),
                    "memory_total": self.cached_specs.get("gpu_total_mb", "N/A")
                }
        except Exception:
            pass

        return {"percent": "N/A", "memory_used": "N/A", "memory_total": self.cached_specs.get("gpu_total_mb", "N/A")}

    def get_battery_metrics(self):
        """Returns battery percentage, plugged status, and time left."""
        try:
            if not hasattr(psutil, "sensors_battery"):
                return None

            battery = psutil.sensors_battery()
            if not battery:
                return None

            return {
                "percent": round(battery.percent, 1),
                "power_plugged": battery.power_plugged,
                "secsleft": battery.secsleft if not battery.power_plugged else "N/A"
            }
        except Exception:
            return None

    def get_top_processes(self, limit=10):
        """Returns top processes with Active Threat Heuristics."""
        try:
            processes = []
            for proc in psutil.process_iter(['pid', 'name', 'cpu_percent', 'memory_percent', 'exe']):
                try:
                    pinfo = proc.info
                    # Evaluate Heuristics
                    exe_path = pinfo.get('exe') or ""
                    is_suspicious = False

                    if exe_path:
                        for bad_path in SUSPICIOUS_PATHS:
                            if bad_path.lower() in exe_path.lower():
                                is_suspicious = True
                                break
                        # Unix hidden paths check (.foldername)
                        if "/." in exe_path:
                            is_suspicious = True

                    pinfo['suspicious'] = is_suspicious
                    processes.append(pinfo)
                except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
                    pass

            # Sort by CPU usage descending
            processes.sort(key=lambda p: p['cpu_percent'] or 0, reverse=True)
            return processes[:limit]
        except Exception:
            return []

    def get_temperatures(self):
        """Attempts to fetch hardware temperatures."""
        try:
            if not hasattr(psutil, "sensors_temperatures"):
                return "N/A"

            temps = psutil.sensors_temperatures()
            if not temps:
                return "N/A"

            if 'coretemp' in temps:
                sum_temp = sum([t.current for t in temps['coretemp']])
                avg_temp = sum_temp / len(temps['coretemp'])
                return round(avg_temp, 1)

            first_sensor_list = list(temps.values())[0]
            if first_sensor_list:
                return round(first_sensor_list[0].current, 1)

            return "N/A"

        except Exception:
            return "N/A"

    def get_fan_speeds(self):
        """Attempts to fetch fan speeds (RPM)."""
        try:
            if not hasattr(psutil, "sensors_fans"):
                return "N/A"

            fans = psutil.sensors_fans()
            if not fans:
                return "N/A"

            first_fan_list = list(fans.values())[0]
            if first_fan_list:
                return first_fan_list[0].current

            return "N/A"

        except Exception:
            return "N/A"

    def get_net_connections(self):
        """
        Fetches active TCP/UDP connections.
        Can be resource-intensive, should be polled infrequently (e.g., 10s).
        Requires elevated privileges on some OSs to see all connections.
        Masks public external IPs for privacy.
        """
        def _mask_ip(ip_str):
            if not ip_str or ip_str == "N/A":
                return "N/A"
            try:
                ip_obj = ipaddress.ip_address(ip_str)
                # If it's a private network, loopback, etc., leave it fully visible
                if ip_obj.is_private or ip_obj.is_loopback:
                    return ip_str
                # Otherwise, mask the last octet (or equivalent for IPv6)
                if ip_obj.version == 4:
                    parts = ip_str.split('.')
                    return f"{parts[0]}.{parts[1]}.{parts[2]}.***"
                else:
                    return "External IPv6 Masked"
            except ValueError:
                return ip_str

        try:
            # Only grab a limited number to avoid massive payloads
            max_conns = 100
            conns = []
            # psutil.net_connections requires root on some systems for 'all' or specific types
            # 'inet' gets IPv4 and IPv6
            for c in psutil.net_connections(kind='inet'):
                # Format: family, type, laddr, raddr, status, pid
                if c.status in ['ESTABLISHED', 'LISTEN']:
                    # Mask remote IPs
                    l_ip = c.laddr.ip if c.laddr else "N/A"
                    l_port = c.laddr.port if c.laddr else ""
                    local = f"{l_ip}:{l_port}" if l_ip != "N/A" else "N/A"

                    r_ip = c.raddr.ip if c.raddr else "N/A"
                    r_port = c.raddr.port if c.raddr else ""
                    masked_r_ip = _mask_ip(r_ip)
                    remote = f"{masked_r_ip}:{r_port}" if r_ip != "N/A" else "N/A"

                    conns.append({
                        "type": "TCP" if c.type == 1 else "UDP",
                        "local": local,
                        "remote": remote,
                        "status": c.status,
                        "pid": c.pid or "N/A"
                    })
                if len(conns) >= max_conns:
                    break
            return conns
        except (psutil.AccessDenied, Exception):
            return []

    def get_deep_specs(self):
        """Fetches raw Motherboard/BIOS and Disk S.M.A.R.T data via subprocess hooks."""
        specs = {
            "bios": "N/A",
            "motherboard": "N/A",
            "disks": [],
            "battery_health": self.cached_specs.get("battery_health", {}),
            "smart_disks": self.cached_specs.get("smart_disks", [])
        }

        try:
            if self.os_platform == 'Windows':
                # Windows WMIC hooks for BIOS and BaseBoard
                bios = subprocess.check_output(['wmic', 'bios', 'get', 'manufacturer,smbiosbiosversion'], shell=True, text=True).split('\n')[1].strip()
                mb = subprocess.check_output(['wmic', 'baseboard', 'get', 'manufacturer,product'], shell=True, text=True).split('\n')[1].strip()
                specs["bios"] = bios if bios else "N/A"
                specs["motherboard"] = mb if mb else "N/A"

                # Windows Disk Drives basic via WMIC
                disks = subprocess.check_output(['wmic', 'diskdrive', 'get', 'model,status'], shell=True, text=True).strip().split('\n')[1:]
                for d in disks:
                    d_clean = d.strip()
                    if d_clean:
                        specs["disks"].append(d_clean)

            elif self.os_platform == 'Linux':
                # Read /sys/class/dmi/id for native DMI tables (requires some read permissions, might fallback)
                try:
                    with open('/sys/class/dmi/id/bios_version', 'r') as f:
                        specs["bios"] = f.read().strip()
                except Exception:
                    pass
                try:
                    with open('/sys/class/dmi/id/board_name', 'r') as f:
                        specs["motherboard"] = f.read().strip()
                except Exception:
                    pass

                # Fetch S.M.A.R.T. data using smartctl if available
                try:
                    # lsblk to get disks
                    lsblk = subprocess.check_output(['lsblk', '-nd', '-o', 'NAME,MODEL'], text=True).strip().split('\n')
                    for line in lsblk:
                        if line:
                            specs["disks"].append(line.strip())
                except Exception:
                    pass
        except Exception:
            pass

        return specs

    def kill_process(self, pid):
        """Attempt to securely kill a process by PID."""
        try:
            p = psutil.Process(pid)
            p.terminate()
            return True, f"Sent terminate signal to PID {pid}"
        except (psutil.NoSuchProcess, psutil.AccessDenied) as e:
            return False, str(e)

    def suspend_process(self, pid):
        """Attempt to securely suspend a process by PID."""
        try:
            p = psutil.Process(pid)
            p.suspend()
            return True, f"Suspended PID {pid}"
        except (psutil.NoSuchProcess, psutil.AccessDenied, AttributeError) as e:
            # AttributeError happens if OS doesn't support suspend
            return False, str(e)

    def resume_process(self, pid):
        """Attempt to securely resume a process by PID."""
        try:
            p = psutil.Process(pid)
            p.resume()
            return True, f"Resumed PID {pid}"
        except (psutil.NoSuchProcess, psutil.AccessDenied, AttributeError) as e:
            return False, str(e)
