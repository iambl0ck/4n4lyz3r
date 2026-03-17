import os
import platform
import time

class NativePoller:
    """
    Handles C-Level native bypassing for extreme performance polling.
    Reads /proc/stat natively on Linux and uses ctypes on Windows to bypass Python wrapper overheads.
    """
    def __init__(self):
        self.os_platform = platform.system()
        self.last_cpu_time = None
        self.last_cpu_idle = None

        # Windows ctypes setup
        self._kernel32 = None
        if self.os_platform == 'Windows':
            try:
                import ctypes
                self._kernel32 = ctypes.windll.kernel32

                class FILETIME(ctypes.Structure):
                    _fields_ = [("dwLowDateTime", ctypes.c_uint),
                                ("dwHighDateTime", ctypes.c_uint)]
                self.FILETIME = FILETIME

            except Exception:
                self._kernel32 = None

    def get_cpu_percent_native(self):
        """
        Calculates CPU usage percentage using native OS hooks.
        Returns None if unsupported, signaling to fall back to psutil.
        """
        if self.os_platform == 'Linux':
            try:
                with open('/proc/stat', 'r') as f:
                    lines = f.readline().split()

                # /proc/stat format: cpu  user nice system idle iowait irq softirq steal guest guest_nice
                if lines[0] == 'cpu':
                    idle = float(lines[4]) + float(lines[5])  # idle + iowait
                    non_idle = sum(float(x) for x in lines[1:4] + lines[6:8])
                    total = idle + non_idle

                    if self.last_cpu_time is not None:
                        total_delta = total - self.last_cpu_time
                        idle_delta = idle - self.last_cpu_idle

                        if total_delta > 0:
                            cpu_usage = 100.0 * (1.0 - idle_delta / total_delta)
                            self.last_cpu_time = total
                            self.last_cpu_idle = idle
                            return round(cpu_usage, 1)

                    self.last_cpu_time = total
                    self.last_cpu_idle = idle
                    return None # First call
            except Exception:
                return None

        elif self.os_platform == 'Windows' and self._kernel32:
            try:
                import ctypes
                idle_time = self.FILETIME()
                kernel_time = self.FILETIME()
                user_time = self.FILETIME()

                success = self._kernel32.GetSystemTimes(ctypes.byref(idle_time),
                                                        ctypes.byref(kernel_time),
                                                        ctypes.byref(user_time))
                if success:
                    def _to_int(ft):
                        return (ft.dwHighDateTime << 32) + ft.dwLowDateTime

                    idle = _to_int(idle_time)
                    sys = _to_int(kernel_time)
                    user = _to_int(user_time)

                    total = sys + user

                    if self.last_cpu_time is not None:
                        total_delta = total - self.last_cpu_time
                        idle_delta = idle - self.last_cpu_idle

                        if total_delta > 0:
                            cpu_usage = 100.0 * (1.0 - idle_delta / total_delta)
                            self.last_cpu_time = total
                            self.last_cpu_idle = idle
                            return round(cpu_usage, 1)

                    self.last_cpu_time = total
                    self.last_cpu_idle = idle
                    return None
            except Exception:
                return None

        return None
