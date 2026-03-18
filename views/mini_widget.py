import customtkinter as ctk

class MiniWidget_4n4lyz3r(ctk.CTkToplevel):
    """
    A minimalist, always-on-top, borderless floating widget
    for 4n4lyz3r to conserve screen and system resources.
    """
    def __init__(self, master, restore_callback, **kwargs):
        super().__init__(master, **kwargs)

        self.restore_callback = restore_callback

        # Window configuration
        self.title("4n4lyz3r PIP")
        self.geometry("250x100")

        # Make borderless and always on top
        self.overrideredirect(True)
        self.attributes("-topmost", True)
        self.configure(fg_color="#121212")

        # Make it draggable
        self.bind("<ButtonPress-1>", self.start_move)
        self.bind("<ButtonRelease-1>", self.stop_move)
        self.bind("<B1-Motion>", self.do_move)

        # Main Frame
        self.main_frame = ctk.CTkFrame(self, fg_color="#1E1E1E", corner_radius=10, border_width=1, border_color="#00FFAA")
        self.main_frame.pack(expand=True, fill="both", padx=5, pady=5)

        # Grid setup
        self.main_frame.columnconfigure(0, weight=1)
        self.main_frame.columnconfigure(1, weight=1)
        self.main_frame.columnconfigure(2, weight=1)
        self.main_frame.rowconfigure(0, weight=1)
        self.main_frame.rowconfigure(1, weight=1)

        # Labels
        font_label = ("Helvetica", 10, "bold")
        font_value = ("Helvetica", 14, "bold")

        self.lbl_cpu_t = ctk.CTkLabel(self.main_frame, text="CPU", font=font_label, text_color="#A9A9A9")
        self.lbl_cpu_t.grid(row=0, column=0, pady=(10, 0))
        self.lbl_cpu_v = ctk.CTkLabel(self.main_frame, text="0%", font=font_value, text_color="#FFFFFF")
        self.lbl_cpu_v.grid(row=1, column=0, pady=(0, 10))

        self.lbl_ram_t = ctk.CTkLabel(self.main_frame, text="RAM", font=font_label, text_color="#A9A9A9")
        self.lbl_ram_t.grid(row=0, column=1, pady=(10, 0))
        self.lbl_ram_v = ctk.CTkLabel(self.main_frame, text="0%", font=font_value, text_color="#FFFFFF")
        self.lbl_ram_v.grid(row=1, column=1, pady=(0, 10))

        self.lbl_temp_t = ctk.CTkLabel(self.main_frame, text="TEMP", font=font_label, text_color="#A9A9A9")
        self.lbl_temp_t.grid(row=0, column=2, pady=(10, 0))
        self.lbl_temp_v = ctk.CTkLabel(self.main_frame, text="N/A", font=font_value, text_color="#FFFFFF")
        self.lbl_temp_v.grid(row=1, column=2, pady=(0, 10))

        # Restore Button overlay (top right)
        self.btn_restore = ctk.CTkButton(
            self.main_frame, text="⛶", width=20, height=20,
            fg_color="transparent", hover_color="#333333",
            text_color="#00FFAA", command=self.restore
        )
        self.btn_restore.place(relx=0.95, rely=0.1, anchor="ne")

        # Initial position variables for dragging
        self._x = 0
        self._y = 0

    def start_move(self, event):
        self._x = event.x
        self._y = event.y

    def stop_move(self, event):
        self._x = None
        self._y = None

    def do_move(self, event):
        if self._x is not None and self._y is not None:
            deltax = event.x - self._x
            deltay = event.y - self._y
            x = self.winfo_x() + deltax
            y = self.winfo_y() + deltay
            self.geometry(f"+{x}+{y}")

    def update_metrics(self, cpu_val, ram_val, temp_val):
        """Updates the minimalist text values."""
        self.lbl_cpu_v.configure(text=f"{cpu_val}%" if cpu_val != 'N/A' else "N/A")
        self.lbl_ram_v.configure(text=f"{ram_val}%" if ram_val != 'N/A' else "N/A")
        self.lbl_temp_v.configure(text=f"{temp_val}°C" if temp_val != 'N/A' else "N/A")

    def restore(self):
        """Triggered when the restore button is clicked."""
        self.destroy()
        self.restore_callback()
