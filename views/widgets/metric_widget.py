import customtkinter as ctk

class SparklineWidget(ctk.CTkCanvas):
    """
    A lightweight, native Canvas-based sparkline to visualize 60 seconds of hardware/network data dynamically.
    Clean Futuristic Glassmorphism aesthetic.
    """
    def __init__(self, master, width=200, height=40, line_color="#00FFAA", bg_color="#1E1E1E", **kwargs):
        super().__init__(master, width=width, height=height, bg=bg_color, highlightthickness=0, **kwargs)
        self.line_color = line_color
        self.width = width
        self.height = height

    def update_sparkline(self, data_points):
        """Redraws the sparkline. Expects a list of floats (len up to 60)."""
        self.delete("all")
        if not data_points or len(data_points) < 2:
            return

        max_val = max(data_points) if max(data_points) > 0 else 1.0 # Avoid div by zero
        # Add a tiny bit of headroom
        max_val = max_val * 1.1

        x_step = self.width / (len(data_points) - 1)
        coords = []

        for i, val in enumerate(data_points):
            x = i * x_step
            # Invert Y because canvas 0 is at the top
            y = self.height - ((val / max_val) * self.height)
            coords.extend([x, y])

        # Draw the line
        self.create_line(coords, fill=self.line_color, width=2, smooth=False, capstyle="round", joinstyle="round")

        # Draw a faint polygon underneath for depth
        poly_coords = [0, self.height] + coords + [self.width, self.height]
        # In Tkinter native canvas, alpha isn't truly supported on polygons without stipples or tricky image hacks,
        # so we'll skip the fill or use a very faint outline. For a clean look, just the thick line is excellent.

class Widget_4n4lyz3r(ctk.CTkFrame):
    """
    A generic reusable widget block for displaying a metric in 4n4lyz3r.
    Modernized layout for "Clean Futuristic Glassmorphism".
    """
    def __init__(self, master, title, has_progress=True, has_sparkline=False, sparkline_color="#00FFAA", **kwargs):
        super().__init__(master, fg_color="#1E1E1E", corner_radius=15, **kwargs)

        # Title Label
        self.title_label = ctk.CTkLabel(
            self, text=title, font=("Helvetica", 14, "bold"), text_color="#A9A9A9"
        )
        self.title_label.pack(pady=(15, 5), padx=20, anchor="w")

        # Value Label
        self.value_label = ctk.CTkLabel(
            self, text="0.0%", font=("Helvetica", 32, "bold"), text_color="#FFFFFF"
        )
        self.value_label.pack(pady=0, padx=20, anchor="w")

        # Sub-value Label (e.g. for Used/Total GB or extra context)
        self.subvalue_label = ctk.CTkLabel(
            self, text="", font=("Helvetica", 12), text_color="#808080"
        )
        self.subvalue_label.pack(pady=(0, 10), padx=20, anchor="w")

        # Progress Bar (optional)
        self.has_progress = has_progress
        if self.has_progress:
            self.progress_bar = ctk.CTkProgressBar(
                self, width=200, height=12, progress_color="#00FFAA", fg_color="#2A2A2A", corner_radius=6
            )
            self.progress_bar.set(0)
            self.progress_bar.pack(pady=(10, 20), padx=20, fill="x")

        # Sparkline (optional)
        self.has_sparkline = has_sparkline
        if self.has_sparkline:
            self.sparkline = SparklineWidget(self, line_color=sparkline_color)
            self.sparkline.pack(pady=(5, 20), padx=20, fill="x")

    def update_data(self, value_text, percent=None, subvalue_text="", sparkline_data=None):
        """Updates the labels, progress bar, and sparkline dynamically."""
        self.value_label.configure(text=value_text)

        if subvalue_text:
            self.subvalue_label.configure(text=subvalue_text)
        else:
            self.subvalue_label.configure(text="")

        if self.has_progress and percent is not None:
            # Handle string 'N/A' gracefully
            try:
                progress_val = float(percent) / 100.0
                self.progress_bar.set(progress_val)
                # Change color based on usage thresholds
                if progress_val > 0.9:
                    self.progress_bar.configure(progress_color="#FF4444")
                elif progress_val > 0.75:
                    self.progress_bar.configure(progress_color="#FFAA00")
                else:
                    self.progress_bar.configure(progress_color="#00FFAA")
            except ValueError:
                self.progress_bar.set(0)

        if self.has_sparkline and sparkline_data is not None:
            self.sparkline.update_sparkline(sparkline_data)
