import customtkinter as ctk

class Widget_4n4lyz3r(ctk.CTkFrame):
    """
    A generic reusable widget block for displaying a metric in 4n4lyz3r.
    Includes a title, a large value label, and an optional progress bar.
    """
    def __init__(self, master, title, has_progress=True, **kwargs):
        super().__init__(master, fg_color="#1E1E1E", corner_radius=10, **kwargs)

        # Title Label
        self.title_label = ctk.CTkLabel(
            self, text=title, font=("Helvetica", 16, "bold"), text_color="#A9A9A9"
        )
        self.title_label.pack(pady=(10, 5), padx=15, anchor="w")

        # Value Label
        self.value_label = ctk.CTkLabel(
            self, text="0.0%", font=("Helvetica", 36, "bold"), text_color="#FFFFFF"
        )
        self.value_label.pack(pady=5, padx=15, anchor="w")

        # Sub-value Label (e.g. for Used/Total GB or extra context)
        self.subvalue_label = ctk.CTkLabel(
            self, text="", font=("Helvetica", 12), text_color="#808080"
        )
        self.subvalue_label.pack(pady=0, padx=15, anchor="w")

        # Progress Bar (optional)
        self.has_progress = has_progress
        if self.has_progress:
            self.progress_bar = ctk.CTkProgressBar(
                self, width=200, height=8, progress_color="#00FFAA", fg_color="#333333"
            )
            self.progress_bar.set(0)
            self.progress_bar.pack(pady=(15, 15), padx=15, fill="x")

    def update_data(self, value_text, percent=None, subvalue_text=""):
        """Updates the labels and progress bar."""
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
