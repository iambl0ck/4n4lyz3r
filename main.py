import sys
import os

# Ensure the root directory is on the path if run outside standard environments
sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))

import socket
from controllers.main_controller import Controller_4n4lyz3r

def ensure_singleton():
    """
    Binds a local socket to a specific port to prevent multiple
    instances of the monitoring dashboard from running simultaneously.
    """
    lock_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    try:
        # Port 44444 chosen arbitrarily for instance locking
        lock_socket.bind(('127.0.0.1', 44444))
        return lock_socket
    except socket.error:
        print("4n4lyz3r is already running. Exiting.")
        sys.exit(0)

def main():
    """
    Entry point for the 4n4lyz3r application.
    Initializes the Controller_4n4lyz3r and starts the dashboard.
    """
    _lock = ensure_singleton()

    controller = Controller_4n4lyz3r()

    # Run the main application loop
    controller.start()

if __name__ == "__main__":
    main()
