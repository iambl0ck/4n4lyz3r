import json
import os
import secrets

CONFIG_FILE = "4n4lyz3r_config.json"

class ConfigManager:
    """
    Manages local application state, API Keys, and remote Fleet nodes.
    Creates a default configuration on the first launch.
    """
    def __init__(self):
        self.config = {
            "local_node": {
                "api_key": secrets.token_urlsafe(32),
                "port": 40404
            },
            "fleet_nodes": [] # List of {"ip": str, "port": int, "api_key": str}
        }
        self.load_config()

    def load_config(self):
        if os.path.exists(CONFIG_FILE):
            try:
                with open(CONFIG_FILE, 'r') as f:
                    saved_config = json.load(f)

                # Merge saved config to keep existing keys and fleet nodes
                if "local_node" in saved_config:
                    self.config["local_node"].update(saved_config["local_node"])
                if "fleet_nodes" in saved_config:
                    self.config["fleet_nodes"] = saved_config["fleet_nodes"]
            except Exception:
                pass # If corrupted, use default

        self.save_config() # Save immediately to ensure it exists

    def save_config(self):
        try:
            with open(CONFIG_FILE, 'w') as f:
                json.dump(self.config, f, indent=4)
        except Exception:
            pass

    def get_local_api_key(self):
        return self.config["local_node"]["api_key"]

    def get_local_port(self):
        return self.config["local_node"]["port"]

    def get_fleet_nodes(self):
        return self.config["fleet_nodes"]

    def add_fleet_node(self, ip, port, api_key):
        # Prevent duplicates by IP:Port
        for node in self.config["fleet_nodes"]:
            if node["ip"] == ip and node["port"] == port:
                return False, "Node already exists."

        self.config["fleet_nodes"].append({
            "ip": ip,
            "port": port,
            "api_key": api_key
        })
        self.save_config()
        return True, "Node added successfully."
