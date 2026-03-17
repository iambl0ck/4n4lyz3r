import psutil
import platform
import time
import collections
import ipaddress
try:
    import GPUtil
    _HAS_GPUTIL = True
except ImportError:
    _HAS_GPUTIL = False

class Model_4n4lyz3r:
    """
    Model class to fetch and process system metrics for 4n4lyz3r.
    Handles fallbacks for OS-specific restrictions gracefully.
    Implements extreme static caching and memory leak prevention.
    """

    def __init__(self):
        self.os_platform = platform.system()
        # Initialize psutil counters to avoid blocking/spikes on first fetch
        psutil.cpu_percent()

        # --- EXTREME CACHING (Static Specs) ---
        self.cached_specs = {}

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

    def get_cpu_metrics(self):
        """Returns CPU usage percentage and pushes to bounded history."""
        try:
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

    def get_top_processes(self, limit=5):
        """Returns top processes sorted by CPU (and optionally memory) usage."""
        try:
            processes = []
            for proc in psutil.process_iter(['pid', 'name', 'cpu_percent', 'memory_percent']):
                try:
                    pinfo = proc.info
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

    def get_all_metrics(self):
        """Fetches and aggregates basic (synchronous) metrics into a single dictionary."""
        # This was used in the MVP, but the controller will use individual async calls.
        return {
            "cpu": self.get_cpu_metrics(),
            "ram": self.get_ram_metrics(),
            "disk": self.get_disk_metrics(),
            "network": self.get_network_metrics(),
            "gpu": self.get_gpu_metrics(),
            "battery": self.get_battery_metrics(),
            "temperature": self.get_temperatures(),
            "fan": self.get_fan_speeds()
        }
