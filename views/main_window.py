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

        # Subtitle
        self.subtitle_label = ctk.CTkLabel(
            self.header_frame, text="SYSTEM HEALTH DASHBOARD", font=("Helvetica", 14), text_color="#555555"
        )
        self.subtitle_label.pack(side="right", pady=10)

        # Main Grid Frame for widgets
        self.main_grid = ctk.CTkFrame(self, fg_color="transparent")
        self.main_grid.pack(expand=True, fill="both", padx=30, pady=10)

        # Grid Configuration (2x2 Layout, and an extra row for temps/fans)
        self.main_grid.columnconfigure(0, weight=1)
        self.main_grid.columnconfigure(1, weight=1)

        # Widgets Initialization
        self.cpu_widget = Widget_4n4lyz3r(self.main_grid, title="CPU USAGE", has_progress=True)
        self.cpu_widget.grid(row=0, column=0, padx=10, pady=10, sticky="nsew")

        self.ram_widget = Widget_4n4lyz3r(self.main_grid, title="RAM USAGE", has_progress=True)
        self.ram_widget.grid(row=0, column=1, padx=10, pady=10, sticky="nsew")

        self.disk_widget = Widget_4n4lyz3r(self.main_grid, title="DISK HEALTH", has_progress=True)
        self.disk_widget.grid(row=1, column=0, padx=10, pady=10, sticky="nsew")

        # Bottom row for Temperature and Fan
        self.bottom_row = ctk.CTkFrame(self.main_grid, fg_color="transparent")
        self.bottom_row.grid(row=1, column=1, padx=10, pady=10, sticky="nsew")
        self.bottom_row.columnconfigure(0, weight=1)
        self.bottom_row.columnconfigure(1, weight=1)

        self.temp_widget = Widget_4n4lyz3r(self.bottom_row, title="CORE TEMP", has_progress=False)
        self.temp_widget.grid(row=0, column=0, padx=5, pady=0, sticky="nsew")

        self.fan_widget = Widget_4n4lyz3r(self.bottom_row, title="FAN RPM", has_progress=False)
        self.fan_widget.grid(row=0, column=1, padx=5, pady=0, sticky="nsew")

        # Warning/Info Footer
        self.footer_label = ctk.CTkLabel(
            self, text="Tip: Run as Administrator/Root to unlock fan speeds and temperatures.",
            font=("Helvetica", 12), text_color="#808080"
        )
        self.footer_label.pack(side="bottom", pady=20)

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
