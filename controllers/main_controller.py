from models.system_monitor import Model_4n4lyz3r
from views.main_window import View_4n4lyz3r

class Controller_4n4lyz3r:
    """
    Main Controller for 4n4lyz3r.
    Handles the synchronization between the Model_4n4lyz3r and the View_4n4lyz3r.
    """
    def __init__(self):
        self.model = Model_4n4lyz3r()
        self.view = View_4n4lyz3r()

        # Refresh rate in milliseconds (1000ms = 1s)
        self.refresh_interval = 1000

    def start(self):
        """Starts the main application loop and the data polling."""
        self.update_loop()
        self.view.mainloop()

    def update_loop(self):
        """Fetches metrics from the model and updates the UI."""
        # 1. Fetch metrics
        metrics = self.model.get_all_metrics()

        # 2. Update view
        self.view.update_ui(metrics)

        # 3. Schedule the next update
        self.view.after(self.refresh_interval, self.update_loop)
