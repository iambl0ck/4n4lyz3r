import psutil
import platform
import time

class Model_4n4lyz3r:
    """
    Model class to fetch and process system metrics for 4n4lyz3r.
    Handles fallbacks for OS-specific restrictions gracefully.
    """

    def __init__(self):
        self.os_platform = platform.system()
        # Initialize psutil counters to avoid blocking/spikes on first fetch
        psutil.cpu_percent()
        self.last_disk_io = psutil.disk_io_counters()
        self.last_disk_time = time.time()

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

    def get_temperatures(self):
        """
        Attempts to fetch hardware temperatures.
        Returns 'N/A' or a dict of temperatures if successful.
        Requires elevated privileges on most OSs.
        """
        try:
            if not hasattr(psutil, "sensors_temperatures"):
                return "N/A"

            temps = psutil.sensors_temperatures()
            if not temps:
                return "N/A"

            # Try to grab the coretemp (common on Intel/Linux) or first available
            if 'coretemp' in temps:
                # Average of core temps
                sum_temp = sum([t.current for t in temps['coretemp']])
                avg_temp = sum_temp / len(temps['coretemp'])
                return round(avg_temp, 1)

            # Fallback to the first sensor found
            first_sensor_list = list(temps.values())[0]
            if first_sensor_list:
                return round(first_sensor_list[0].current, 1)

            return "N/A"

        except Exception:
            return "N/A"

    def get_fan_speeds(self):
        """
        Attempts to fetch fan speeds (RPM).
        Returns 'N/A' if inaccessible.
        """
        try:
            if not hasattr(psutil, "sensors_fans"):
                return "N/A"

            fans = psutil.sensors_fans()
            if not fans:
                return "N/A"

            # Try to return the first available fan speed
            first_fan_list = list(fans.values())[0]
            if first_fan_list:
                return first_fan_list[0].current

            return "N/A"

        except Exception:
            return "N/A"

    def get_all_metrics(self):
        """Fetches and aggregates all metrics into a single dictionary."""
        return {
            "cpu": self.get_cpu_metrics(),
            "ram": self.get_ram_metrics(),
            "disk": self.get_disk_metrics(),
            "temperature": self.get_temperatures(),
            "fan": self.get_fan_speeds()
        }
