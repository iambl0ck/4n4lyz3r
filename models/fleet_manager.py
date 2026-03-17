import json
import urllib.request
from urllib.error import URLError
import concurrent.futures

class FleetManagerPoller:
    """
    Zero-Dependency Remote Node Poller.
    Pings the /api/health endpoint of remote 4n4lyz3r fleet nodes asynchronously.
    """
    @staticmethod
    def poll_node(ip, port, api_key):
        """
        Fetches the JSON snapshot from a remote node securely.
        Returns (is_online: bool, snapshot: dict)
        """
        url = f"http://{ip}:{port}/api/health"
        try:
            req = urllib.request.Request(
                url,
                headers={'Authorization': f'Bearer {api_key}'}
            )

            # Strict 3-second timeout
            with urllib.request.urlopen(req, timeout=3.0) as response:
                if response.status == 200:
                    data = json.loads(response.read().decode('utf-8'))
                    return True, data

        except (URLError, json.JSONDecodeError, Exception):
            pass # Fail silently

        return False, {}

    @staticmethod
    def poll_all(nodes_list):
        """
        Iterates over a list of configured nodes in parallel and returns an updated dictionary of snapshots.
        Takes: [{"ip": "1.2.3.4", "port": 40404, "api_key": "xxx"}]
        Returns: { "1.2.3.4:40404": {"online": bool, "cpu": ..., "ram": ...} }
        """
        results = {}

        def _fetch(node):
            ip = node.get("ip")
            port = node.get("port")
            key = node.get("api_key")
            if not ip or not port or not key:
                return None

            node_id = f"{ip}:{port}"
            is_online, snapshot = FleetManagerPoller.poll_node(ip, port, key)
            return node_id, is_online, snapshot

        with concurrent.futures.ThreadPoolExecutor(max_workers=min(10, len(nodes_list) or 1)) as executor:
            futures = [executor.submit(_fetch, node) for node in nodes_list]
            for future in concurrent.futures.as_completed(futures):
                res = future.result()
                if res:
                    node_id, is_online, snapshot = res
                    results[node_id] = {
                        "online": is_online,
                        "snapshot": snapshot
                    }

        return results
