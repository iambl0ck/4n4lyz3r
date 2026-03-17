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

        # PIP / Mini-Widget Button
        self.pip_button = ctk.CTkButton(
            self.header_frame, text="⛶ PIP Mode", width=80, height=28,
            fg_color="#00FFAA", text_color="#121212", hover_color="#00CC88"
        )
        self.pip_button.pack(side="right", padx=(10, 0), pady=10)

        # Main Content Frame (Tabview)
        self.tabview = ctk.CTkTabview(self, fg_color="#1E1E1E", segmented_button_selected_color="#00FFAA", segmented_button_selected_hover_color="#00CC88")
        self.tabview.pack(expand=True, fill="both", padx=30, pady=10)

        # Tabs
        self.tab_dashboard = self.tabview.add("Dashboard")
        self.tab_netsec = self.tabview.add("Net-Sec")

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
        self.cpu_widget = Widget_4n4lyz3r(self.main_grid, title="CPU USAGE", has_progress=True)
        self.cpu_widget.grid(row=0, column=0, padx=10, pady=10, sticky="nsew")

        self.ram_widget = Widget_4n4lyz3r(self.main_grid, title="RAM USAGE", has_progress=True)
        self.ram_widget.grid(row=0, column=1, padx=10, pady=10, sticky="nsew")

        self.disk_widget = Widget_4n4lyz3r(self.main_grid, title="DISK IO", has_progress=True)
        self.disk_widget.grid(row=1, column=0, padx=10, pady=10, sticky="nsew")

        self.net_widget = Widget_4n4lyz3r(self.main_grid, title="NETWORK", has_progress=False)
        self.net_widget.grid(row=1, column=1, padx=10, pady=10, sticky="nsew")

        self.gpu_widget = Widget_4n4lyz3r(self.main_grid, title="GPU USAGE", has_progress=True)
        self.gpu_widget.grid(row=2, column=0, padx=10, pady=10, sticky="nsew")

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
        self.proc_frame = ctk.CTkFrame(self.content_frame, fg_color="#1E1E1E", width=250, corner_radius=10)
        self.proc_frame.pack(side="right", fill="y", padx=(10, 0))
        self.proc_frame.pack_propagate(False)

        self.proc_title = ctk.CTkLabel(self.proc_frame, text="TOP RESOURCE HOGS", font=("Helvetica", 12, "bold"), text_color="#00FFAA")
        self.proc_title.pack(pady=10)

        self.proc_labels = []
        for i in range(5):
            lbl = ctk.CTkLabel(self.proc_frame, text="...", font=("Consolas", 10), text_color="#A9A9A9", anchor="w", justify="left")
            lbl.pack(fill="x", padx=10, pady=5)
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
        self.connections_list = ctk.CTkScrollableFrame(self.netsec_frame, fg_color="#121212", corner_radius=10)
        self.connections_list.pack(expand=True, fill="both", padx=10, pady=10)

        # Toast Notification Frame (hidden initially)
        self.toast_frame = ctk.CTkFrame(self, fg_color="#FF4444", corner_radius=10, width=300, height=60)
        self.toast_label = ctk.CTkLabel(self.toast_frame, text="", font=("Helvetica", 14, "bold"), text_color="#FFFFFF")
        self.toast_label.pack(expand=True, padx=20, pady=10)
        self._toast_timer = None

        # Cache for Net-Sec to avoid unnecessary redraws
        self._last_net_conns = None

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

        disk_subvalue = f"{disk_used} GB / {disk_total} GB" if disk_pct != 'N/A' else ""
        if read_speed_mb != 'N/A' and write_speed_mb != 'N/A':
            disk_subvalue += f" (R: {read_speed_mb} MB/s W: {write_speed_mb} MB/s)"

        self.disk_widget.update_data(
            f"{disk_pct}%" if disk_pct != 'N/A' else 'N/A',
            percent=disk_pct if disk_pct != 'N/A' else 0,
            subvalue_text=disk_subvalue
        )

        # Update Temperature
        temp_val = metrics.get('temperature', 'N/A')
        # If N/A or lock icon needed, handle gracefully
        self.temp_widget.update_data(
            f"{temp_val}°C" if temp_val != 'N/A' else "🔒 N/A"
        )

        # Update Fan
        fan_val = metrics.get('fan', 'N/A')
        self.fan_widget.update_data(
            f"{fan_val} RPM" if fan_val != 'N/A' else "🔒 N/A"
        )

        # Update Network
        net_dict = metrics.get('network', {})
        up_mb = net_dict.get('up_speed_mb', 'N/A')
        down_mb = net_dict.get('down_speed_mb', 'N/A')
        self.net_widget.update_data(
            f"DL: {down_mb} MB/s",
            subvalue_text=f"UL: {up_mb} MB/s" if up_mb != 'N/A' else ""
        )

        # Update GPU
        gpu_dict = metrics.get('gpu', {})
        gpu_pct = gpu_dict.get('percent', 'N/A')
        gpu_used = gpu_dict.get('memory_used', 'N/A')
        gpu_total = gpu_dict.get('memory_total', 'N/A')
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

        # Update Top Processes
        procs = metrics.get('top_processes', [])
        for i, lbl in enumerate(self.proc_labels):
            if i < len(procs):
                p = procs[i]
                name = p.get('name', 'Unknown')[:10].ljust(10)
                cpu = p.get('cpu_percent', 0)
                mem = p.get('memory_percent', 0)
                lbl.configure(text=f"{name} | {cpu:.1f}% CPU | {mem:.1f}% RAM")
            else:
                lbl.configure(text="")

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
