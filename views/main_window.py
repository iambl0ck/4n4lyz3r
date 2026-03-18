import customtkinter as ctk
from views.widgets.metric_widget import Widget_4n4lyz3r

class View_4n4lyz3r(ctk.CTk):
    """
    The main Dashboard Window for 4n4lyz3r.
    Follows a minimalist, dark-themed cyberpunk aesthetic.
    """
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        # Window configuration
        self.title("4n4lyz3r - System Health & Monitor")
        self.geometry("900x600")

        # Set theme and base colors
        ctk.set_appearance_mode("dark")
        ctk.set_default_color_theme("green")

        # Window properties
        self.minsize(800, 500)
        self.configure(fg_color="#121212")

        # Top Header Frame
        self.header_frame = ctk.CTkFrame(self, fg_color="#121212", corner_radius=0)
        self.header_frame.pack(fill="x", pady=20, padx=30)

        # Branding / Title
        self.title_label = ctk.CTkLabel(
            self.header_frame, text="4n4lyz3r", font=("Courier New", 36, "bold"), text_color="#00FFAA"
        )
        self.title_label.pack(side="left")

        # Battery Status Label (dynamically shown/hidden)
        self.battery_label = ctk.CTkLabel(
            self.header_frame, text="", font=("Helvetica", 12), text_color="#FFFFFF", fg_color="#333333", corner_radius=5
        )
        self.battery_label.pack(side="right", padx=(10, 0), pady=10, ipadx=10, ipady=5)

        # Update Available Button (Hidden by default, shown by controller)
        self.btn_update = ctk.CTkButton(
            self.header_frame, text="🚀 UPDATE AVAILABLE", width=120, height=28,
            fg_color="#FF4444", text_color="#FFFFFF", hover_color="#CC0000"
        )

        # PIP / Mini-Widget Button
        self.pip_button = ctk.CTkButton(
            self.header_frame, text="⛶ PIP Mode", width=80, height=28,
            fg_color="#00FFAA", text_color="#121212", hover_color="#00CC88"
        )
        self.pip_button.pack(side="right", padx=(10, 0), pady=10)

        # Main Content Frame (Tabview)
        # Increase internal padding and size
        self.tabview = ctk.CTkTabview(
            self, fg_color="#1A1A1A", corner_radius=15,
            segmented_button_selected_color="#00FFAA",
            segmented_button_selected_hover_color="#00CC88",
            text_color="#FFFFFF"
        )
        self.tabview.pack(expand=True, fill="both", padx=40, pady=15)

        # Tabs
        self.tab_dashboard = self.tabview.add("Dashboard")
        self.tab_netsec = self.tabview.add("Net-Sec")
        self.tab_defense = self.tabview.add("Active Defense")
        self.tab_hw = self.tabview.add("Deep Specs")
        self.tab_fleet = self.tabview.add("Fleet")
        self.tab_settings = self.tabview.add("Settings")

        # Callbacks (assigned by controller)
        self.cmd_kill_process = None
        self.cmd_suspend_process = None
        self.cmd_add_fleet_node = None
        self.cmd_save_ai_key = None
        self.cmd_ai_audit = None

        # Dashboard Tab Content Frame
        self.content_frame = ctk.CTkFrame(self.tab_dashboard, fg_color="transparent")
        self.content_frame.pack(expand=True, fill="both")

        # Main Grid Frame for hardware widgets
        self.main_grid = ctk.CTkFrame(self.content_frame, fg_color="transparent")
        self.main_grid.pack(side="left", expand=True, fill="both", padx=(0, 10))

        # Grid Configuration (2x3 Layout now)
        self.main_grid.columnconfigure(0, weight=1)
        self.main_grid.columnconfigure(1, weight=1)

        # Widgets Initialization
        # Added Sparklines and padded grids
        self.cpu_widget = Widget_4n4lyz3r(self.main_grid, title="CPU USAGE", has_progress=True)
        self.cpu_widget.grid(row=0, column=0, padx=15, pady=15, sticky="nsew")

        self.ram_widget = Widget_4n4lyz3r(self.main_grid, title="RAM USAGE", has_progress=True)
        self.ram_widget.grid(row=0, column=1, padx=15, pady=15, sticky="nsew")

        self.disk_widget = Widget_4n4lyz3r(self.main_grid, title="DISK I/O", has_progress=False, has_sparkline=True, sparkline_color="#FFAA00")
        self.disk_widget.grid(row=1, column=0, padx=15, pady=15, sticky="nsew")

        self.net_widget = Widget_4n4lyz3r(self.main_grid, title="NETWORK", has_progress=False, has_sparkline=True, sparkline_color="#00FFAA")
        self.net_widget.grid(row=1, column=1, padx=15, pady=15, sticky="nsew")

        self.gpu_widget = Widget_4n4lyz3r(self.main_grid, title="GPU USAGE", has_progress=True)
        self.gpu_widget.grid(row=2, column=0, padx=15, pady=15, sticky="nsew")

        # Bottom row for Temperature and Fan
        self.bottom_row = ctk.CTkFrame(self.main_grid, fg_color="transparent")
        self.bottom_row.grid(row=2, column=1, padx=10, pady=10, sticky="nsew")
        self.bottom_row.columnconfigure(0, weight=1)
        self.bottom_row.columnconfigure(1, weight=1)

        self.temp_widget = Widget_4n4lyz3r(self.bottom_row, title="CORE TEMP", has_progress=False)
        self.temp_widget.grid(row=0, column=0, padx=5, pady=0, sticky="nsew")

        self.fan_widget = Widget_4n4lyz3r(self.bottom_row, title="FAN RPM", has_progress=False)
        self.fan_widget.grid(row=0, column=1, padx=5, pady=0, sticky="nsew")

        # Top Processes Right Panel
        self.proc_frame = ctk.CTkFrame(self.content_frame, fg_color="#1E1E1E", width=300, corner_radius=15)
        self.proc_frame.pack(side="right", fill="y", padx=(10, 0), pady=15)
        self.proc_frame.pack_propagate(False)

        self.proc_title = ctk.CTkLabel(self.proc_frame, text="TOP RESOURCE HOGS", font=("Helvetica", 14, "bold"), text_color="#00FFAA")
        self.proc_title.pack(pady=20)

        self.proc_labels = []
        for i in range(5):
            lbl = ctk.CTkLabel(self.proc_frame, text="...", font=("Consolas", 12), text_color="#A9A9A9", anchor="w", justify="left")
            lbl.pack(fill="x", padx=20, pady=10)
            self.proc_labels.append(lbl)

        # Warning/Info Footer
        self.footer_label = ctk.CTkLabel(
            self, text="Tip: Run as Administrator/Root to unlock fan speeds and temperatures.",
            font=("Helvetica", 12), text_color="#808080"
        )
        self.footer_label.pack(side="bottom", pady=20)

        # Net-Sec Tab Content Frame
        self.netsec_frame = ctk.CTkFrame(self.tab_netsec, fg_color="transparent")
        self.netsec_frame.pack(expand=True, fill="both")

        self.netsec_title = ctk.CTkLabel(self.netsec_frame, text="ACTIVE NETWORK CONNECTIONS", font=("Helvetica", 16, "bold"), text_color="#00FFAA")
        self.netsec_title.pack(pady=10)

        # Add a scrollable frame for connections
        self.connections_list = ctk.CTkScrollableFrame(
            self.netsec_frame, fg_color="#121212", corner_radius=10,
            scrollbar_button_color="#2A2A2A", scrollbar_button_hover_color="#00FFAA"
        )
        self.connections_list.pack(expand=True, fill="both", padx=10, pady=10)

        # Toast Notification Frame (hidden initially)
        self.toast_frame = ctk.CTkFrame(self, fg_color="#FF4444", corner_radius=10, width=300, height=60)
        self.toast_label = ctk.CTkLabel(self.toast_frame, text="", font=("Helvetica", 14, "bold"), text_color="#FFFFFF")
        self.toast_label.pack(expand=True, padx=20, pady=10)
        self._toast_timer = None

        # Active Defense Tab Content
        self.defense_frame = ctk.CTkFrame(self.tab_defense, fg_color="transparent")
        self.defense_frame.pack(expand=True, fill="both")
        self.defense_title = ctk.CTkLabel(self.defense_frame, text="PROCESS MANAGER (ACTIVE HEURISTICS)", font=("Helvetica", 16, "bold"), text_color="#FF4444")
        self.defense_title.pack(pady=10)
        self.defense_list = ctk.CTkScrollableFrame(
            self.defense_frame, fg_color="#121212", corner_radius=10,
            scrollbar_button_color="#2A2A2A", scrollbar_button_hover_color="#00FFAA"
        )
        self.defense_list.pack(expand=True, fill="both", padx=10, pady=10)
        self._last_procs = None

        # Deep Specs Tab Content
        self.hw_frame = ctk.CTkScrollableFrame(
            self.tab_hw, fg_color="transparent",
            scrollbar_button_color="#2A2A2A", scrollbar_button_hover_color="#00FFAA"
        )
        self.hw_frame.pack(expand=True, fill="both")
        self.hw_title = ctk.CTkLabel(self.hw_frame, text="RAW HARDWARE & FIRMWARE SPECS", font=("Helvetica", 16, "bold"), text_color="#00FFAA")
        self.hw_title.pack(pady=10)

        self.lbl_bios = ctk.CTkLabel(self.hw_frame, text="BIOS: Fetching...", font=("Consolas", 14), text_color="#FFFFFF")
        self.lbl_bios.pack(pady=5)
        self.lbl_mb = ctk.CTkLabel(self.hw_frame, text="Motherboard: Fetching...", font=("Consolas", 14), text_color="#FFFFFF")
        self.lbl_mb.pack(pady=5)

        # Battery Health Frame
        self.bat_frame = ctk.CTkFrame(self.hw_frame, fg_color="#1E1E1E", corner_radius=10)
        self.bat_frame.pack(fill="x", padx=20, pady=10)
        self.lbl_bat_title = ctk.CTkLabel(self.bat_frame, text="BATTERY WEAR LEVEL & HEALTH", font=("Helvetica", 14, "bold"), text_color="#00FFAA")
        self.lbl_bat_title.pack(pady=10)
        self.lbl_bat_data = ctk.CTkLabel(self.bat_frame, text="Fetching Analytics...", font=("Consolas", 12), text_color="#A9A9A9")
        self.lbl_bat_data.pack(pady=10)

        # Disks Frame
        self.disks_frame = ctk.CTkFrame(self.hw_frame, fg_color="#1E1E1E", corner_radius=10)
        self.disks_frame.pack(fill="x", padx=20, pady=10)
        self.lbl_disks_title = ctk.CTkLabel(self.disks_frame, text="S.M.A.R.T. DISK DIAGNOSTICS", font=("Helvetica", 14, "bold"), text_color="#00FFAA")
        self.lbl_disks_title.pack(pady=10)
        self.lbl_disks_list = ctk.CTkLabel(self.disks_frame, text="Fetching Diagnostics...", font=("Consolas", 12), text_color="#A9A9A9", justify="left")
        self.lbl_disks_list.pack(pady=10, padx=20, anchor="w")

        # Export Actions Frame
        self.actions_frame = ctk.CTkFrame(self.hw_frame, fg_color="transparent")
        self.actions_frame.pack(fill="x", padx=20, pady=20)

        self.btn_export = ctk.CTkButton(
            self.actions_frame, text="Export System Report", font=("Helvetica", 14, "bold"),
            fg_color="#00FFAA", text_color="#121212", hover_color="#00CC88"
        )
        self.btn_export.pack(side="left", padx=10)

        self.btn_ai_audit = ctk.CTkButton(
            self.actions_frame, text="🤖 Analyze with AI", font=("Helvetica", 14, "bold"),
            fg_color="#9900FF", text_color="#FFFFFF", hover_color="#7A00CC", command=self._handle_ai_audit
        )
        self.btn_ai_audit.pack(side="left", padx=10)

        # AI Audit Output Area
        self.txt_ai_output = ctk.CTkTextbox(self.hw_frame, height=100, fg_color="#1E1E1E", text_color="#00FFAA", font=("Consolas", 12), state="disabled")
        self.txt_ai_output.pack(fill="x", padx=20, pady=5)

        # Fleet Tab Content
        self.fleet_frame = ctk.CTkFrame(self.tab_fleet, fg_color="transparent")
        self.fleet_frame.pack(expand=True, fill="both")
        self.fleet_title = ctk.CTkLabel(self.fleet_frame, text="FLEET MANAGEMENT", font=("Helvetica", 16, "bold"), text_color="#00FFAA")
        self.fleet_title.pack(pady=10)

        # Local Node Info
        self.local_node_frame = ctk.CTkFrame(self.fleet_frame, fg_color="#1E1E1E", corner_radius=10)
        self.local_node_frame.pack(fill="x", padx=20, pady=5)
        self.lbl_local_api = ctk.CTkLabel(self.local_node_frame, text="Local API Key: Fetching...", font=("Consolas", 12), text_color="#FFFFFF")
        self.lbl_local_api.pack(pady=5, padx=10, anchor="w")
        self.lbl_local_port = ctk.CTkLabel(self.local_node_frame, text="Local Port: 40404", font=("Consolas", 12), text_color="#A9A9A9")
        self.lbl_local_port.pack(pady=5, padx=10, anchor="w")

        # Add Node Form
        self.add_node_frame = ctk.CTkFrame(self.fleet_frame, fg_color="#121212", corner_radius=10)
        self.add_node_frame.pack(fill="x", padx=20, pady=10)

        self.entry_ip = ctk.CTkEntry(self.add_node_frame, placeholder_text="Remote IP (e.g. 192.168.1.100)", width=200)
        self.entry_ip.pack(side="left", padx=10, pady=10)

        self.entry_key = ctk.CTkEntry(self.add_node_frame, placeholder_text="Remote API Key", width=300)
        self.entry_key.pack(side="left", padx=10, pady=10)

        self.btn_add_node = ctk.CTkButton(self.add_node_frame, text="Add Node", fg_color="#00FFAA", text_color="#121212", hover_color="#00CC88", command=self._handle_add_node)
        self.btn_add_node.pack(side="left", padx=10, pady=10)

        # Fleet Grid
        self.fleet_grid = ctk.CTkScrollableFrame(
            self.fleet_frame, fg_color="transparent",
            scrollbar_button_color="#2A2A2A", scrollbar_button_hover_color="#00FFAA"
        )
        self.fleet_grid.pack(expand=True, fill="both", padx=10, pady=10)
        self._last_fleet_nodes = {}

        # Settings Tab Content
        self.settings_frame = ctk.CTkFrame(self.tab_settings, fg_color="transparent")
        self.settings_frame.pack(expand=True, fill="both")
        self.settings_title = ctk.CTkLabel(self.settings_frame, text="APPLICATION SETTINGS", font=("Helvetica", 16, "bold"), text_color="#00FFAA")
        self.settings_title.pack(pady=10)

        self.ai_key_frame = ctk.CTkFrame(self.settings_frame, fg_color="#1E1E1E", corner_radius=10)
        self.ai_key_frame.pack(fill="x", padx=20, pady=10)

        self.lbl_ai_key = ctk.CTkLabel(self.ai_key_frame, text="OpenAI API Key (Required for 🤖 Analyze with AI):", font=("Helvetica", 12), text_color="#A9A9A9")
        self.lbl_ai_key.pack(pady=5, padx=10, anchor="w")

        self.entry_ai_key = ctk.CTkEntry(self.ai_key_frame, placeholder_text="sk-...", width=400, show="*")
        self.entry_ai_key.pack(side="left", padx=10, pady=10)

        self.btn_save_ai_key = ctk.CTkButton(self.ai_key_frame, text="Save Key", fg_color="#00FFAA", text_color="#121212", hover_color="#00CC88", command=self._handle_save_ai_key)
        self.btn_save_ai_key.pack(side="left", padx=10, pady=10)

        # Cache for Net-Sec to avoid unnecessary redraws
        self._last_net_conns = None

    def _handle_ai_audit(self):
        """Passes the request to the controller."""
        if self.cmd_ai_audit:
            self.txt_ai_output.configure(state="normal")
            self.txt_ai_output.delete("0.0", "end")
            self.txt_ai_output.insert("0.0", "Contacting AI Auditor. Please wait...")
            self.txt_ai_output.configure(state="disabled")
            self.btn_ai_audit.configure(state="disabled", text="Thinking...")
            self.cmd_ai_audit()

    def _handle_save_ai_key(self):
        """Passes the key save action to the controller."""
        key = self.entry_ai_key.get().strip()
        if self.cmd_save_ai_key:
            self.cmd_save_ai_key(key)
            self.entry_ai_key.delete(0, 'end')

    def _handle_add_node(self):
        """Passes input values to the controller callback."""
        ip = self.entry_ip.get().strip()
        key = self.entry_key.get().strip()
        if ip and key and self.cmd_add_fleet_node:
            self.cmd_add_fleet_node(ip, 40404, key)
            self.entry_ip.delete(0, 'end')
            self.entry_key.delete(0, 'end')

    def show_toast(self, message):
        """Displays a sliding toast notification for alerts."""
        self.toast_label.configure(text=message)
        # Place it near bottom right
        self.toast_frame.place(relx=0.98, rely=0.95, anchor="se")

        if self._toast_timer is not None:
            self.after_cancel(self._toast_timer)

        # Hide after 4 seconds
        self._toast_timer = self.after(4000, self.hide_toast)

    def hide_toast(self):
        """Hides the toast notification."""
        self.toast_frame.place_forget()

    def show_update_button(self, url):
        """Dynamically unhides the update button and binds the browser launch."""
        import webbrowser
        self.btn_update.configure(command=lambda: webbrowser.open(url))
        self.btn_update.pack(side="right", padx=(10, 0), pady=10)

    def update_ui(self, metrics):
        """
        Takes a metrics dictionary from the Controller and updates the widgets.
        """
        # Update CPU
        cpu_val = metrics.get('cpu', 'N/A')
        self.cpu_widget.update_data(
            f"{cpu_val}%" if cpu_val != 'N/A' else 'N/A',
            percent=cpu_val if cpu_val != 'N/A' else 0
        )

        # Update RAM
        ram_dict = metrics.get('ram', {})
        ram_pct = ram_dict.get('percent', 'N/A')
        ram_used = ram_dict.get('used_gb', 'N/A')
        ram_total = ram_dict.get('total_gb', 'N/A')
        self.ram_widget.update_data(
            f"{ram_pct}%" if ram_pct != 'N/A' else 'N/A',
            percent=ram_pct if ram_pct != 'N/A' else 0,
            subvalue_text=f"{ram_used} GB / {ram_total} GB" if ram_pct != 'N/A' else ""
        )

        # Update Disk
        disk_dict = metrics.get('disk', {})
        disk_pct = disk_dict.get('percent', 'N/A')
        disk_used = disk_dict.get('used_gb', 'N/A')
        disk_total = disk_dict.get('total_gb', 'N/A')
        read_speed_mb = disk_dict.get('read_speed_mb', 'N/A')
        write_speed_mb = disk_dict.get('write_speed_mb', 'N/A')
        hist_r = disk_dict.get('history_r', [])

        disk_subvalue = f"{disk_used} GB / {disk_total} GB" if disk_pct != 'N/A' else ""
        if read_speed_mb != 'N/A' and write_speed_mb != 'N/A':
            disk_subvalue += f" (R: {read_speed_mb} MB/s W: {write_speed_mb} MB/s)"

        self.disk_widget.update_data(
            f"{disk_pct}%" if disk_pct != 'N/A' else 'N/A',
            percent=disk_pct if disk_pct != 'N/A' else 0,
            subvalue_text=disk_subvalue,
            sparkline_data=hist_r
        )

        # Update Temperature
        temp_val = metrics.get('temperature', 'N/A')
        if temp_val in ["N/A", "OEM Locked"]:
            self.temp_widget.update_data(f"🔒 {temp_val}")
        else:
            self.temp_widget.update_data(f"{temp_val}°C")

        # Update Fan
        fan_val = metrics.get('fan', 'N/A')
        if fan_val in ["N/A", "OEM Locked"]:
            self.fan_widget.update_data(f"🔒 {fan_val}")
        else:
            self.fan_widget.update_data(f"{fan_val} RPM")

        # Update Network
        net_dict = metrics.get('network', {})
        up_mb = net_dict.get('up_speed_mb', 'N/A')
        down_mb = net_dict.get('down_speed_mb', 'N/A')
        hist_dl = net_dict.get('history_dl', [])
        self.net_widget.update_data(
            f"DL: {down_mb} MB/s",
            subvalue_text=f"UL: {up_mb} MB/s" if up_mb != 'N/A' else "",
            sparkline_data=hist_dl
        )

        # Update GPU
        gpu_dict = metrics.get('gpu', {})
        gpu_pct = gpu_dict.get('percent', 'N/A')
        gpu_used = gpu_dict.get('memory_used', 'N/A')
        gpu_total = gpu_dict.get('memory_total', 'N/A')
        gpu_name = gpu_dict.get('name', 'GPU')
        self.gpu_widget.title_label.configure(text=str(gpu_name).upper())
        self.gpu_widget.update_data(
            f"{gpu_pct}%" if gpu_pct != 'N/A' else 'N/A',
            percent=gpu_pct if gpu_pct != 'N/A' else 0,
            subvalue_text=f"VRAM: {gpu_used} MB / {gpu_total} MB" if gpu_pct != 'N/A' else "GPU: N/A"
        )

        # Update Battery
        bat_dict = metrics.get('battery')
        if bat_dict:
            bat_pct = bat_dict.get('percent', 0)
            plugged = bat_dict.get('power_plugged', False)
            secsleft = bat_dict.get('secsleft', "N/A")

            icon = "🔌" if plugged else "🔋"
            text_val = f"{icon} {bat_pct}%"

            if not plugged and isinstance(secsleft, (int, float)) and secsleft > 0:
                # Convert seconds to HH:MM format
                hours, remainder = divmod(secsleft, 3600)
                minutes, _ = divmod(remainder, 60)
                text_val += f" ({int(hours)}h {int(minutes)}m)"

            self.battery_label.configure(text=text_val)
        else:
            # Hide on desktop / if not available
            self.battery_label.pack_forget()

        # Update Top Processes (Dashboard View)
        procs = metrics.get('top_processes', [])
        for i, lbl in enumerate(self.proc_labels):
            if i < len(procs) and i < 5:
                p = procs[i]
                name = p.get('name', 'Unknown')[:10].ljust(10)
                cpu = p.get('cpu_percent', 0)
                mem = p.get('memory_percent', 0)
                suspicious = p.get('suspicious', False)
                text_color = "#FF4444" if suspicious else "#A9A9A9"
                lbl.configure(text=f"{name} | {cpu:.1f}% CPU | {mem:.1f}% RAM", text_color=text_color)
            else:
                lbl.configure(text="")

        # Update Active Defense Tab (if visible)
        if self.tabview.get() == "Active Defense":
            if procs != self._last_procs:
                self._last_procs = procs.copy() if procs else []

                # Clear existing
                for widget in self.defense_list.winfo_children():
                    widget.destroy()

                # Repopulate
                for p in procs:
                    pid = p.get('pid', 'N/A')
                    name = p.get('name', 'Unknown')
                    cpu = p.get('cpu_percent', 0)
                    mem = p.get('memory_percent', 0)
                    suspicious = p.get('suspicious', False)

                    row_frame = ctk.CTkFrame(self.defense_list, fg_color="transparent")
                    row_frame.pack(fill="x", pady=2)

                    t_color = "#FF4444" if suspicious else "#FFFFFF"
                    tag = "[SUSPICIOUS] " if suspicious else ""
                    lbl = ctk.CTkLabel(row_frame, text=f"{tag}PID: {pid} | {name} | CPU: {cpu:.1f}% | RAM: {mem:.1f}%", font=("Consolas", 12), text_color=t_color)
                    lbl.pack(side="left", padx=10)

                    if pid != 'N/A' and self.cmd_kill_process:
                        btn_kill = ctk.CTkButton(row_frame, text="KILL", width=50, height=24, fg_color="#FF4444", hover_color="#CC0000", command=lambda p=pid: self.cmd_kill_process(p))
                        btn_kill.pack(side="right", padx=5)

                    if pid != 'N/A' and self.cmd_suspend_process:
                        btn_sus = ctk.CTkButton(row_frame, text="SUSPEND", width=60, height=24, fg_color="#FFAA00", text_color="#121212", hover_color="#CC8800", command=lambda p=pid: self.cmd_suspend_process(p))
                        btn_sus.pack(side="right", padx=5)

        # Update Deep Specs (if tab is visible)
        deep_specs = metrics.get('deep_specs', {})
        if self.tabview.get() == "Deep Specs":
            self.lbl_bios.configure(text=f"BIOS: {deep_specs.get('bios', 'N/A')}")
            self.lbl_mb.configure(text=f"Motherboard: {deep_specs.get('motherboard', 'N/A')}")

            # Battery Wear Analytics
            bat_health = deep_specs.get("battery_health", {})
            b_status = bat_health.get("status", "N/A (Desktop)")
            if b_status == "Found":
                wear = bat_health.get("wear_level", "N/A")
                hpct = bat_health.get("health_pct", "N/A")
                grade = bat_health.get("grade", "N/A")
                self.lbl_bat_data.configure(text=f"Health Grade: {grade}\nTotal Wear Level: {wear}%\nUsable Charge Capacity: {hpct}%")
            else:
                self.lbl_bat_data.configure(text=f"Status: {b_status}")

            # S.M.A.R.T Disk Analytics
            smart_disks = deep_specs.get("smart_disks", [])
            if smart_disks:
                disk_text_lines = []
                for d in smart_disks:
                    model = d.get('model', 'Unknown')
                    status = d.get('status', 'Unknown')
                    grade = d.get('grade', 'Unknown')
                    disk_text_lines.append(f"Model: {model}\nStatus: {status}  |  Grade: {grade}\n")

                self.lbl_disks_list.configure(text="\n".join(disk_text_lines))
            else:
                self.lbl_disks_list.configure(text="No deep diagnostics found or permission denied.")

        # Update Fleet Management (if tab is visible)
        fleet_data = metrics.get('fleet_data', {})
        if self.tabview.get() == "Fleet":
            if fleet_data != self._last_fleet_nodes:
                self._last_fleet_nodes = fleet_data.copy() if fleet_data else {}

                # Clear existing
                for widget in self.fleet_grid.winfo_children():
                    widget.destroy()

                # Repopulate
                for node_id, data in fleet_data.items():
                    is_online = data.get("online", False)
                    snap = data.get("snapshot", {})

                    status_color = "#00FFAA" if is_online else "#FF4444"
                    status_text = "🟢 Online" if is_online else "🔴 Offline"
                    cpu = snap.get("cpu", "N/A") if is_online else "---"

                    ram_dict = snap.get("ram", {}) if is_online else {}
                    ram = ram_dict.get("percent", "N/A") if isinstance(ram_dict, dict) else "---"

                    # Mini Card
                    card = ctk.CTkFrame(self.fleet_grid, fg_color="#1E1E1E", corner_radius=10, border_width=1, border_color=status_color)
                    card.pack(fill="x", pady=5, padx=10)

                    lbl_node = ctk.CTkLabel(card, text=f"Node: {node_id}  |  {status_text}", font=("Helvetica", 14, "bold"), text_color="#FFFFFF")
                    lbl_node.pack(side="left", padx=10, pady=10)

                    lbl_stats = ctk.CTkLabel(card, text=f"CPU: {cpu}%  |  RAM: {ram}%", font=("Consolas", 14), text_color="#A9A9A9")
                    lbl_stats.pack(side="right", padx=10, pady=10)

        # Update Net-Sec Connections (if the tab is visible)
        # To avoid massive UI updates, only refresh if the list changed
        conns = metrics.get('net_connections', [])

        if self.tabview.get() == "Net-Sec":
            # Check if the list of connections actually changed
            if conns != self._last_net_conns:
                self._last_net_conns = conns.copy() if conns else []

                # Clear existing children
                for widget in self.connections_list.winfo_children():
                    widget.destroy()

                # Repopulate
                for c in conns:
                    t = c.get('type', '')
                    l = c.get('local', '')
                    r = c.get('remote', '')
                    s = c.get('status', '')
                    pid = c.get('pid', '')
                    row_text = f"[{t}] {l}  =>  {r}  |  {s}  |  PID: {pid}"

                    # Use slightly different colors based on status
                    t_color = "#00FFAA" if s == "ESTABLISHED" else "#A9A9A9"

                    lbl = ctk.CTkLabel(self.connections_list, text=row_text, font=("Consolas", 12), text_color=t_color, anchor="w")
                    lbl.pack(fill="x", pady=2, padx=5)
