import threading
import time
import gc
try:
    import pystray
    _HAS_PYSTRAY = True
except Exception:
    _HAS_PYSTRAY = False

import tkinter.filedialog as filedialog
import webbrowser
from PIL import Image, ImageDraw, ImageFont
from models.system_monitor import Model_4n4lyz3r
from models.report_generator import ReportGenerator
from models.update_checker import OTAUpdateChecker
from models.fleet_manager import FleetManagerPoller
from models.ai_auditor import AIAuditor
from views.main_window import View_4n4lyz3r
from views.mini_widget import MiniWidget_4n4lyz3r
from utils.logger import Logger_4n4lyz3r
from utils.config import ConfigManager
from services.api_server import ApiServerService

class Controller_4n4lyz3r:
    """
    Main Controller for 4n4lyz3r.
    Handles the synchronization between the Model_4n4lyz3r and the View_4n4lyz3r.
    Implements multi-threading, headless tray mode, explicit GC, and Fleet APIs.
    """
    def __init__(self):
        self.model = Model_4n4lyz3r()
        self.view = View_4n4lyz3r()
        self.mini_widget = None
        self.logger = Logger_4n4lyz3r()
        self.config = ConfigManager()
        self.is_pip_mode = False
        self.is_tray_mode = False
        self.running = True
        self.ui_update_job = None
        self.tray_icon = None

        # Thread lock for safely updating shared metrics dictionary
        self.metrics_lock = threading.Lock()
        self.metrics = {
            "cpu": "N/A", "ram": {}, "disk": {}, "network": {}, "gpu": {},
            "battery": None, "temperature": "N/A", "fan": "N/A", "top_processes": [],
            "net_connections": [], "deep_specs": {}, "fleet_data": {}
        }

        # Initialize REST API Server Daemon
        self.api_server = ApiServerService(
            port=self.config.get_local_port(),
            get_api_key_callback=self.config.get_local_api_key,
            get_snapshot_callback=self._get_current_snapshot,
            logger=self.logger
        )

        # Wire up view callbacks
        self.view.cmd_kill_process = self.handle_kill_process
        self.view.cmd_suspend_process = self.handle_suspend_process
        self.view.cmd_add_fleet_node = self.handle_add_fleet_node
        self.view.cmd_save_ai_key = self.handle_save_ai_key
        self.view.cmd_ai_audit = self.handle_ai_audit
        self.view.btn_export.configure(command=self.handle_export_report)

        # Setup View static data
        self.view.lbl_local_api.configure(text=f"Local API Key: {self.config.get_local_api_key()}")
        self.view.lbl_local_port.configure(text=f"Local Port: {self.config.get_local_port()}")

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
        # Start Fleet API background listener
        self.api_server.start()

        threading.Thread(target=self.poll_1s, daemon=True).start()
        threading.Thread(target=self.poll_2s, daemon=True).start()
        threading.Thread(target=self.poll_5s, daemon=True).start()
        threading.Thread(target=self.poll_10s, daemon=True).start()

        # Schedule the OTA Update Checker (Runs ONCE 5 seconds after launch)
        ota_timer = threading.Timer(5.0, self.check_for_ota_updates)
        ota_timer.daemon = True
        ota_timer.start()

    def _get_current_snapshot(self):
        """Helper to return a thread-safe snapshot for the API server."""
        with self.metrics_lock:
            return self.model.generate_snapshot(self.metrics)

    def check_for_ota_updates(self):
        """Pings the GitHub API for newer releases silently."""
        has_update, tag, url = OTAUpdateChecker.check_for_updates()

        if has_update:
            msg = f"Update Available: {tag} is out!"
            self.logger.log_info(f"OTA Update Detected: {tag} -> {url}")

            def _notify_update():
                self.view.show_toast(msg)
                # Show dynamic update button in header
                self.view.show_update_button(url)

            self.view.after(0, _notify_update)

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
        """Disk, Battery, Net Connections, Deep Specs, Fleet Data - every 10 seconds"""
        while self.running:
            disk = self.model.get_disk_metrics()
            battery = self.model.get_battery_metrics()
            # Net connections and Deep specs can be heavy, poll only every 10s
            net_conns = self.model.get_net_connections()
            deep_specs = self.model.get_deep_specs()

            # Poll fleet nodes asynchronously
            fleet_nodes = self.config.get_fleet_nodes()
            fleet_data = FleetManagerPoller.poll_all(fleet_nodes) if fleet_nodes else {}

            with self.metrics_lock:
                self.metrics["disk"] = disk
                self.metrics["battery"] = battery
                self.metrics["net_connections"] = net_conns
                self.metrics["deep_specs"] = deep_specs
                self.metrics["fleet_data"] = fleet_data
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
        """Restores the main full dashboard window from PIP."""
        self.is_pip_mode = False
        self.view.deiconify()  # Show main window

    def _create_tray_icon(self):
        """Programmatically generates a minimalist dark/neon-green icon for the tray."""
        # Create a 64x64 square
        image = Image.new('RGB', (64, 64), color=(18, 18, 18))  # #121212
        dc = ImageDraw.Draw(image)
        # Draw a neon green border
        dc.rectangle([0, 0, 63, 63], outline=(0, 255, 170), width=4)  # #00FFAA

        try:
            # Try to load a generic sans-serif font
            font = ImageFont.truetype("arial.ttf", 48)
        except Exception:
            # Fallback to default
            font = ImageFont.load_default()

        # Draw the "4"
        text = "4"
        bbox = dc.textbbox((0, 0), text, font=font)
        text_w = bbox[2] - bbox[0]
        text_h = bbox[3] - bbox[1]
        x = (64 - text_w) / 2
        # Adjust Y slightly depending on font rendering, simple center is fine for default
        y = (64 - text_h) / 2 - 8
        dc.text((x, y), text, fill=(0, 255, 170), font=font)

        return image

    def minimize_to_tray(self):
        """Hides the main window, cancels UI updates, explicitly triggers GC, and spawns the tray icon."""
        self.view.withdraw()
        if self.is_pip_mode and self.mini_widget:
            self.mini_widget.destroy()
            self.is_pip_mode = False

        self.is_tray_mode = True

        # Suspend the GUI loop
        if self.ui_update_job is not None:
            self.view.after_cancel(self.ui_update_job)
            self.ui_update_job = None

        # Explicit garbage collection to prevent memory leaks during long background uptimes
        gc.collect()

        # Spawn the tray icon in a separate thread (pystray blocks)
        if _HAS_PYSTRAY:
            def tray_setup():
                menu = pystray.Menu(
                    pystray.MenuItem("Restore 4n4lyz3r", self.restore_from_tray, default=True),
                    pystray.MenuItem("Quit", self.on_closing)
                )
                image = self._create_tray_icon()
                self.tray_icon = pystray.Icon("4n4lyz3r", image, "4n4lyz3r - Monitoring", menu)
                self.tray_icon.run()

            threading.Thread(target=tray_setup, daemon=True).start()
        else:
            self.logger.log_info("System tray is not supported in this environment. Running headless.")

    def restore_from_tray(self, icon=None, item=None):
        """Restores the main window from the system tray and resumes UI updates."""
        if self.tray_icon:
            self.tray_icon.stop()
            self.tray_icon = None

        self.is_tray_mode = False

        # Schedule the UI restore on the main Tkinter thread to prevent cross-thread crashes
        def _do_restore():
            self.view.deiconify()
            self.update_ui_loop()

        self.view.after(0, _do_restore)

    def start(self):
        """Starts the main application loop and the UI update polling."""
        # Intercept the 'X' button to minimize to tray instead of quitting
        self.view.protocol("WM_DELETE_WINDOW", self.minimize_to_tray)
        self.update_ui_loop()
        self.view.mainloop()

    def update_ui_loop(self):
        """Periodically refreshes the active UI from the shared metrics dictionary."""
        # If in tray mode, do not render UI (saves CPU/GPU)
        if self.is_tray_mode:
            return

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
        self.ui_update_job = self.view.after(1000, self.update_ui_loop)

    def handle_kill_process(self, pid):
        """Callback to securely kill a process by PID from the UI."""
        success, msg = self.model.kill_process(pid)
        if success:
            self.logger.log_info(f"User Action: Killed {msg}")
            self.view.show_toast(f"Killed PID {pid}")
        else:
            self.logger.log_error(f"User Action: Kill Failed - {msg}")
            self.view.show_toast(f"Failed to kill PID {pid} (Access Denied?)")

    def handle_suspend_process(self, pid):
        """Callback to securely suspend a process by PID from the UI."""
        success, msg = self.model.suspend_process(pid)
        if success:
            self.logger.log_info(f"User Action: Suspended {msg}")
            self.view.show_toast(f"Suspended PID {pid}")
        else:
            self.logger.log_error(f"User Action: Suspend Failed - {msg}")
            self.view.show_toast(f"Failed to suspend PID {pid}")

    def handle_export_report(self):
        """
        Handles the export of the system report.
        Uses a file dialog on the main thread, then spawns a background thread to format and write the file.
        """
        filetypes = [
            ('Text Document', '*.txt'),
            ('JSON Data', '*.json'),
            ('All Files', '*.*')
        ]

        filepath = filedialog.asksaveasfilename(
            title="Export 4n4lyz3r System Report",
            defaultextension=".txt",
            filetypes=filetypes,
            initialfile=f"4n4lyz3r_report_{time.strftime('%Y%m%d_%H%M%S')}"
        )

        if not filepath:
            return # User cancelled

        with self.metrics_lock:
            snapshot = self.model.generate_snapshot(self.metrics)

        def _write_report():
            if filepath.endswith('.json'):
                success, msg = ReportGenerator.generate_json(snapshot, filepath)
            else:
                success, msg = ReportGenerator.generate_txt(snapshot, filepath)

            def _notify():
                if success:
                    self.logger.log_info(f"System report exported to {filepath}")
                    self.view.show_toast("Report Exported Successfully!")
                else:
                    self.logger.log_error(f"Report export failed: {msg}")
                    self.view.show_toast("Report Export Failed")

            # Post toast notification safely back to main thread
            self.view.after(0, _notify)

        threading.Thread(target=_write_report, daemon=True).start()

    def handle_add_fleet_node(self, ip, port, api_key):
        """Callback to add a new fleet node to the config."""
        success, msg = self.config.add_fleet_node(ip, port, api_key)
        if success:
            self.logger.log_info(f"Added new Fleet Node: {ip}:{port}")
            self.view.show_toast("Fleet Node Added!")
        else:
            self.view.show_toast(msg)

    def handle_save_ai_key(self, key):
        """Saves the AI API key to the config."""
        self.config.set_ai_api_key(key)
        self.view.show_toast("AI API Key Saved!")

    def handle_ai_audit(self):
        """Triggers the background AI Audit and updates the text box when complete."""
        api_key = self.config.get_ai_api_key()

        with self.metrics_lock:
            snapshot = self.model.generate_snapshot(self.metrics)

        def _run_audit():
            success, msg = AIAuditor.audit_snapshot(api_key, snapshot)

            def _update_ui():
                self.view.txt_ai_output.configure(state="normal")
                self.view.txt_ai_output.delete("0.0", "end")
                self.view.txt_ai_output.insert("0.0", msg)
                self.view.txt_ai_output.configure(state="disabled")
                self.view.btn_ai_audit.configure(state="normal", text="🤖 Analyze with AI")

                if success:
                    self.logger.log_info("AI Audit Complete.")
                else:
                    self.logger.log_error(msg)

            self.view.after(0, _update_ui)

        threading.Thread(target=_run_audit, daemon=True).start()

    def on_closing(self, icon=None, item=None):
        """Gracefully shuts down the application and background threads."""
        self.running = False
        self.api_server.stop()
        if self.tray_icon:
            self.tray_icon.stop()

        # Ensure UI destruction happens on the main thread safely
        def _do_close():
            self.view.quit()
            self.view.destroy()

        self.view.after(0, _do_close)
