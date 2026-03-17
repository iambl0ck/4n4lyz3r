import threading
import time
from models.system_monitor import Model_4n4lyz3r
from views.main_window import View_4n4lyz3r
from views.mini_widget import MiniWidget_4n4lyz3r
from utils.logger import Logger_4n4lyz3r

class Controller_4n4lyz3r:
    """
    Main Controller for 4n4lyz3r.
    Handles the synchronization between the Model_4n4lyz3r and the View_4n4lyz3r.
    Implements multi-threading and smart polling to prevent GUI blocking.
    """
    def __init__(self):
        self.model = Model_4n4lyz3r()
        self.view = View_4n4lyz3r()
        self.mini_widget = None
        self.logger = Logger_4n4lyz3r()
        self.is_pip_mode = False
        self.running = True

        # Thread lock for safely updating shared metrics dictionary
        self.metrics_lock = threading.Lock()
        self.metrics = {
            "cpu": "N/A", "ram": {}, "disk": {}, "network": {}, "gpu": {},
            "battery": None, "temperature": "N/A", "fan": "N/A", "top_processes": [],
            "net_connections": []
        }

        # Alert Cooldowns (in seconds, 5 mins = 300)
        self.alert_cooldowns = {
            "cpu": 0,
            "ram": 0,
            "temp": 0
        }
        self.cooldown_duration = 300

        # Bind the PIP button
        self.view.pip_button.configure(command=self.toggle_pip_mode)

        # Start background polling threads
        self.start_threads()

    def start_threads(self):
        """Initializes background daemon threads for different polling intervals."""
        threading.Thread(target=self.poll_1s, daemon=True).start()
        threading.Thread(target=self.poll_2s, daemon=True).start()
        threading.Thread(target=self.poll_5s, daemon=True).start()
        threading.Thread(target=self.poll_10s, daemon=True).start()

    def poll_1s(self):
        """CPU, Network, Temp, Fan - every 1 second"""
        while self.running:
            cpu = self.model.get_cpu_metrics()
            net = self.model.get_network_metrics()
            temp = self.model.get_temperatures()
            fan = self.model.get_fan_speeds()

            with self.metrics_lock:
                self.metrics["cpu"] = cpu
                self.metrics["network"] = net
                self.metrics["temperature"] = temp
                self.metrics["fan"] = fan
            time.sleep(1)

    def poll_2s(self):
        """RAM, GPU - every 2 seconds"""
        while self.running:
            ram = self.model.get_ram_metrics()
            gpu = self.model.get_gpu_metrics()

            with self.metrics_lock:
                self.metrics["ram"] = ram
                self.metrics["gpu"] = gpu
            time.sleep(2)

    def poll_5s(self):
        """Top Processes - every 5 seconds"""
        while self.running:
            top_procs = self.model.get_top_processes(limit=5)
            with self.metrics_lock:
                self.metrics["top_processes"] = top_procs
            time.sleep(5)

    def poll_10s(self):
        """Disk, Battery, Net Connections - every 10 seconds"""
        while self.running:
            disk = self.model.get_disk_metrics()
            battery = self.model.get_battery_metrics()
            # Net connections can be heavy, poll only every 10s
            net_conns = self.model.get_net_connections()

            with self.metrics_lock:
                self.metrics["disk"] = disk
                self.metrics["battery"] = battery
                self.metrics["net_connections"] = net_conns
            time.sleep(10)

    def check_alerts(self, cpu, ram, temp):
        """Evaluates hardware metrics and triggers toast/logs if over thresholds."""
        current_time = time.time()

        # Helper to log asynchronously to avoid any UI thread blocking
        def _async_log(msg):
            threading.Thread(target=self.logger.log_alert, args=(msg,), daemon=True).start()

        # Check CPU (> 90%)
        if isinstance(cpu, (int, float)) and cpu > 90.0:
            if current_time - self.alert_cooldowns["cpu"] > self.cooldown_duration:
                msg = f"High CPU Usage Detected: {cpu}%"
                self.view.show_toast(msg)
                _async_log(msg)
                self.alert_cooldowns["cpu"] = current_time

        # Check RAM (> 95%)
        if isinstance(ram, dict) and 'percent' in ram:
            ram_pct = ram['percent']
            if isinstance(ram_pct, (int, float)) and ram_pct > 95.0:
                if current_time - self.alert_cooldowns["ram"] > self.cooldown_duration:
                    msg = f"High RAM Usage Detected: {ram_pct}%"
                    self.view.show_toast(msg)
                    _async_log(msg)
                    self.alert_cooldowns["ram"] = current_time

        # Check Temperature (> 85°C)
        if isinstance(temp, (int, float)) and temp > 85.0:
            if current_time - self.alert_cooldowns["temp"] > self.cooldown_duration:
                msg = f"High Core Temperature: {temp}°C"
                self.view.show_toast(msg)
                _async_log(msg)
                self.alert_cooldowns["temp"] = current_time

    def toggle_pip_mode(self):
        """Switches to Mini-Widget (Picture-in-Picture) mode."""
        self.is_pip_mode = True
        self.view.withdraw()  # Hide main window

        if self.mini_widget is None or not self.mini_widget.winfo_exists():
            self.mini_widget = MiniWidget_4n4lyz3r(self.view, self.restore_main_window)

    def restore_main_window(self):
        """Restores the main full dashboard window."""
        self.is_pip_mode = False
        self.view.deiconify()  # Show main window

    def start(self):
        """Starts the main application loop and the UI update polling."""
        # Clean up threads on exit
        self.view.protocol("WM_DELETE_WINDOW", self.on_closing)
        self.update_ui_loop()
        self.view.mainloop()

    def update_ui_loop(self):
        """Periodically refreshes the active UI from the shared metrics dictionary."""
        with self.metrics_lock:
            current_metrics = self.metrics.copy()

        cpu = current_metrics.get("cpu", "N/A")
        ram = current_metrics.get("ram", {})
        temp = current_metrics.get("temperature", "N/A")

        # Run alert checks
        self.check_alerts(cpu, ram, temp)

        if self.is_pip_mode and self.mini_widget and self.mini_widget.winfo_exists():
            # Update only essential stats for the mini widget
            ram_pct = ram.get("percent", "N/A") if isinstance(ram, dict) else "N/A"
            self.mini_widget.update_metrics(cpu, ram_pct, temp)
        elif not self.is_pip_mode:
            # Update full dashboard
            self.view.update_ui(current_metrics)

        # Refresh UI every 1 second (this doesn't block as data fetching is threaded)
        self.view.after(1000, self.update_ui_loop)

    def on_closing(self):
        """Gracefully shuts down the background threads."""
        self.running = False
        self.view.destroy()
