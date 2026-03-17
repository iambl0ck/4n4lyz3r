import sys
import os

# Ensure the root directory is on the path if run outside standard environments
sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))

from controllers.main_controller import Controller_4n4lyz3r

def main():
    """
    Entry point for the 4n4lyz3r application.
    Initializes the Controller_4n4lyz3r and starts the dashboard.
    """
    controller = Controller_4n4lyz3r()

    # Run the main application loop
    controller.start()

if __name__ == "__main__":
    main()
