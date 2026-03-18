import logging
import logging.handlers
import os

class Logger_4n4lyz3r:
    """
    Handles background event logging for the 4n4lyz3r application.
    Uses a RotatingFileHandler to keep the log file size under 5MB (with 1 backup).
    """
    def __init__(self, log_file="4n4lyz3r_events.log"):
        self.logger = logging.getLogger("4n4lyz3r_Logger")
        self.logger.setLevel(logging.INFO)

        # Avoid adding multiple handlers if instantiated more than once
        if not self.logger.handlers:
            # 5 MB = 5 * 1024 * 1024 bytes
            handler = logging.handlers.RotatingFileHandler(
                log_file, maxBytes=5 * 1024 * 1024, backupCount=1
            )
            formatter = logging.Formatter(
                '%(asctime)s - [%(levelname)s] - %(message)s',
                datefmt='%Y-%m-%d %H:%M:%S'
            )
            handler.setFormatter(formatter)
            self.logger.addHandler(handler)

    def log_alert(self, message):
        """Logs a high-priority system anomaly or alert."""
        self.logger.warning(f"ALERT: {message}")

    def log_info(self, message):
        """Logs general system information."""
        self.logger.info(message)

    def log_error(self, message):
        """Logs application or system errors."""
        self.logger.error(f"ERROR: {message}")
