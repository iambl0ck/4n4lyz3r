import subprocess
import platform
import os
import re
from utils.helpers import run_hidden_subprocess

class HardwareHealthAnalyzer:
    """
    Handles deep hardware diagnostics for Battery Wear Levels and S.M.A.R.T Disk Health.
    These calls are OS-native and can be slow, so they should be run asynchronously.
    """
    def __init__(self):
        self.os_platform = platform.system()

    def _get_battery_health_grade(self, percentage):
        if percentage >= 90:
            return "🟢 Perfect"
        elif percentage >= 70:
            return "🟡 Good"
        else:
            return "🔴 Replace"

    def analyze_battery(self):
        """
        Fetches Battery Design Capacity vs. Full Charge Capacity to calculate wear level.
        Returns a dict: {'status': str, 'wear_level': float, 'grade': str}
        """
        result = {"status": "N/A (Desktop)", "wear_level": 100.0, "grade": ""}

        try:
            if self.os_platform == "Windows":
                # wmic path Win32_Battery get DesignCapacity, FullChargeCapacity
                output_res = run_hidden_subprocess(['wmic', 'path', 'Win32_Battery', 'get', 'DesignCapacity,FullChargeCapacity'], timeout=3)
                if output_res.returncode == 0:
                    lines = [line.strip() for line in output_res.stdout.split('\n') if line.strip()]
                    if len(lines) > 1:
                        parts = lines[1].split()
                        if len(parts) >= 2:
                            design = float(parts[0])
                            full = float(parts[1])
                            if design > 0:
                                health_pct = (full / design) * 100.0
                                health_pct = min(100.0, health_pct) # Sometimes full > design slightly
                                result = {
                                    "status": "Found",
                                    "wear_level": round(100.0 - health_pct, 1),
                                    "health_pct": round(health_pct, 1),
                                    "grade": self._get_battery_health_grade(health_pct)
                                }

            elif self.os_platform == "Linux":
                # Check /sys/class/power_supply/BAT*
                bat_dir = "/sys/class/power_supply/"
                if os.path.exists(bat_dir):
                    batteries = [d for d in os.listdir(bat_dir) if d.startswith('BAT')]
                    if batteries:
                        bat_path = os.path.join(bat_dir, batteries[0])
                        try:
                            with open(os.path.join(bat_path, "energy_full_design"), 'r') as f:
                                design = float(f.read().strip())
                            with open(os.path.join(bat_path, "energy_full"), 'r') as f:
                                full = float(f.read().strip())

                            if design > 0:
                                health_pct = (full / design) * 100.0
                                health_pct = min(100.0, health_pct)
                                result = {
                                    "status": "Found",
                                    "wear_level": round(100.0 - health_pct, 1),
                                    "health_pct": round(health_pct, 1),
                                    "grade": self._get_battery_health_grade(health_pct)
                                }
                        except Exception:
                            # Fallback if energy attributes don't exist (some use charge_full_design)
                            try:
                                with open(os.path.join(bat_path, "charge_full_design"), 'r') as f:
                                    design = float(f.read().strip())
                                with open(os.path.join(bat_path, "charge_full"), 'r') as f:
                                    full = float(f.read().strip())

                                if design > 0:
                                    health_pct = (full / design) * 100.0
                                    health_pct = min(100.0, health_pct)
                                    result = {
                                        "status": "Found",
                                        "wear_level": round(100.0 - health_pct, 1),
                                        "health_pct": round(health_pct, 1),
                                        "grade": self._get_battery_health_grade(health_pct)
                                    }
                            except Exception:
                                pass

            elif self.os_platform == "Darwin":
                # system_profiler SPPowerDataType
                output_res = run_hidden_subprocess(['system_profiler', 'SPPowerDataType'], timeout=3)

                if output_res.returncode == 0:
                    output = output_res.stdout
                    # We can grab maximum capacity % directly on newer macOS or parse full/design
                    max_cap_match = re.search(r"Maximum Capacity:\s+(\d+)%", output)
                    if max_cap_match:
                        health_pct = float(max_cap_match.group(1))
                        result = {
                            "status": "Found",
                            "wear_level": round(100.0 - health_pct, 1),
                            "health_pct": round(health_pct, 1),
                            "grade": self._get_battery_health_grade(health_pct)
                        }
                    else:
                        # Older macOS parsing (Charge Information: Full Charge Capacity)
                        full_match = re.search(r"Full Charge Capacity \(mAh\):\s+(\d+)", output)
                        if full_match:
                            # We might not have design capacity easily without ioreg,
                            # but if we just have full, we'll mark as found but unknown health.
                            result = {"status": "Found", "wear_level": "N/A", "health_pct": "N/A", "grade": "Unknown"}
        except Exception:
            pass

        return result

    def analyze_disks(self):
        """
        Fetches S.M.A.R.T. status grades natively.
        Returns a list of dicts: [{'model': str, 'status': str, 'grade': str}]
        """
        disks = []
        try:
            if self.os_platform == "Windows":
                # wmic diskdrive get Model, Status
                output_res = run_hidden_subprocess(['wmic', 'diskdrive', 'get', 'Model,Status'], timeout=3)
                if output_res.returncode == 0:
                    lines = [line.strip() for line in output_res.stdout.split('\n') if line.strip()]
                    # First line is header
                    for line in lines[1:]:
                        # Status is typically the last word (OK, Pred Fail, Error, etc.)
                        parts = line.rsplit(maxsplit=1)
                        if len(parts) == 2:
                            model = parts[0].strip()
                            status = parts[1].strip().upper()

                            grade = "🟢 Healthy" if status == "OK" else ("🔴 Failing" if "FAIL" in status else "🟡 Warning")
                            disks.append({
                                "model": model,
                                "status": status,
                                "grade": grade
                            })

            elif self.os_platform == "Linux" or self.os_platform == "Darwin":
                # Check for smartctl
                try:
                    check_res = run_hidden_subprocess(['smartctl', '-h'], timeout=2)
                    if check_res.returncode not in [0, 1]: # Depending on OS smartctl -h might exit 1
                        raise FileNotFoundError
                except Exception:
                    return [{"model": "Unknown", "status": "smartmontools not installed", "grade": "Unknown"}]

                target_disks = []

                if self.os_platform == "Linux":
                    # Use lsblk to find block devices
                    output_res = run_hidden_subprocess(['lsblk', '-nd', '-o', 'NAME,MODEL'], timeout=3)
                    if output_res.returncode == 0:
                        lines = [line.strip() for line in output_res.stdout.split('\n') if line.strip()]
                        for line in lines:
                            parts = line.split(maxsplit=1)
                            if len(parts) >= 1:
                                dev = parts[0]
                                model = parts[1] if len(parts) > 1 else dev
                                target_disks.append((f'/dev/{dev}', model))
                else:
                    # macOS: Use diskutil list
                    output_res = run_hidden_subprocess(['diskutil', 'list'], timeout=3)
                    if output_res.returncode == 0:
                        # Extract /dev/disk0, /dev/disk1, etc.
                        for line in output_res.stdout.split('\n'):
                            if line.startswith('/dev/disk') and '(internal' in line:
                                parts = line.split()
                                dev = parts[0]
                                target_disks.append((dev, "macOS Internal Disk"))

                for dev_path, model in target_disks:
                    try:
                        # Requires root for smartctl
                        smart_out_res = run_hidden_subprocess(['smartctl', '-H', dev_path], timeout=5)
                        if smart_out_res.returncode == 0:
                            if "PASSED" in smart_out_res.stdout.upper() or "OK" in smart_out_res.stdout.upper():
                                grade = "🟢 Healthy"
                                status = "OK"
                            else:
                                grade = "🔴 Failing"
                                status = "FAILED"
                        else:
                            if smart_out_res.returncode == 1 or smart_out_res.returncode == 2:
                                status = "Permission Denied (Run as Root)"
                                grade = "Unknown"
                            else:
                                status = "Warning/Failing"
                                grade = "🔴 Failing"
                    except Exception:
                        status = "Unknown"
                        grade = "Unknown"

                    disks.append({
                        "model": model,
                        "status": status,
                        "grade": grade
                    })

        except Exception:
            return [{"model": "Unknown", "status": "Error fetching SMART data", "grade": "Unknown"}]

        return disks
