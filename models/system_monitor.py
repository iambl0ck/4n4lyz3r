import psutil
import platform
import time
try:
    import GPUtil
    _HAS_GPUTIL = True
except ImportError:
    _HAS_GPUTIL = False

class Model_4n4lyz3r:
    """
    Model class to fetch and process system metrics for 4n4lyz3r.
    Handles fallbacks for OS-specific restrictions gracefully.
    """

    def __init__(self):
        self.os_platform = platform.system()
        # Initialize psutil counters to avoid blocking/spikes on first fetch
        psutil.cpu_percent()

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
            except Exception:
                self.has_gpu = False

    def get_cpu_metrics(self):
        """Returns CPU usage percentage."""
        try:
            return psutil.cpu_percent(interval=None)
        except Exception:
            return "N/A"

    def get_ram_metrics(self):
        """Returns RAM usage percentage and total/used memory in GB."""
        try:
            mem = psutil.virtual_memory()
            total_gb = mem.total / (1024 ** 3)
            used_gb = mem.used / (1024 ** 3)
            return {
                "percent": mem.percent,
                "used_gb": round(used_gb, 2),
                "total_gb": round(total_gb, 2)
            }
        except Exception:
            return {"percent": "N/A", "used_gb": "N/A", "total_gb": "N/A"}

    def get_disk_metrics(self):
        """Returns Disk usage percentage and total/used space for the main partition, plus read/write speeds."""
        try:
            # Check the root partition ('/' on Linux/Mac, 'C:\\' on Windows)
            path = '/' if self.os_platform != 'Windows' else 'C:\\'
            disk = psutil.disk_usage(path)
            total_gb = disk.total / (1024 ** 3)
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
                "total_gb": round(total_gb, 2),
                "read_speed_mb": round(read_speed_mb, 2),
                "write_speed_mb": round(write_speed_mb, 2)
            }
        except Exception:
            return {
                "percent": "N/A", "used_gb": "N/A", "total_gb": "N/A",
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
                    "memory_total": round(gpu.memoryTotal, 1)
                }
        except Exception:
            pass

        return {"percent": "N/A", "memory_used": "N/A", "memory_total": "N/A"}

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
