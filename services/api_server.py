from http.server import BaseHTTPRequestHandler, HTTPServer
import json
import threading

class ApiHandler(BaseHTTPRequestHandler):
    """
    Handles secure REST API requests for Remote Node Monitoring.
    Validates the 'Authorization: Bearer <key>' header against the ConfigManager's local API key.
    """
    def do_GET(self):
        # Allow only the /api/health endpoint
        if self.path != '/api/health':
            self.send_response(404)
            self.end_headers()
            return

        # Authentication
        auth_header = self.headers.get('Authorization')
        expected_key = self.server.get_api_key()

        if not auth_header or not auth_header.startswith('Bearer ') or auth_header.split('Bearer ')[1] != expected_key:
            self.send_response(401)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            self.wfile.write(json.dumps({"error": "Unauthorized"}).encode())
            return

        # Authorized - Return Snapshot
        snapshot = self.server.get_snapshot()
        self.send_response(200)
        self.send_header('Content-type', 'application/json')
        self.end_headers()
        self.wfile.write(json.dumps(snapshot).encode())

    def log_message(self, format, *args):
        # Silence default http.server logging to prevent stdout bloat
        pass

class FleetServer(HTTPServer):
    """
    Custom HTTPServer that allows injecting the ConfigManager key and the current metrics snapshot.
    """
    def __init__(self, server_address, handler_class, get_api_key_callback, get_snapshot_callback):
        super().__init__(server_address, handler_class)
        self.get_api_key = get_api_key_callback
        self.get_snapshot = get_snapshot_callback

class ApiServerService:
    """
    Manages the background daemon threading for the Fleet Server.
    Zero-bloat architecture using built-in http.server.
    """
    def __init__(self, port, get_api_key_callback, get_snapshot_callback, logger=None):
        self.port = port
        self.get_api_key_callback = get_api_key_callback
        self.get_snapshot_callback = get_snapshot_callback
        self.logger = logger
        self.server = None
        self.server_thread = None

    def start(self):
        try:
            self.server = FleetServer(('0.0.0.0', self.port), ApiHandler, self.get_api_key_callback, self.get_snapshot_callback)
            if self.logger:
                self.logger.log_info(f"Fleet API Server started natively on port {self.port}")

            self.server_thread = threading.Thread(target=self.server.serve_forever, daemon=True)
            self.server_thread.start()
        except OSError as e:
            # Usually 'Address already in use'
            if self.logger:
                self.logger.log_error(f"Fleet API Server failed to bind port {self.port}: {e}")

    def stop(self):
        if self.server:
            self.server.shutdown()
            self.server.server_close()
