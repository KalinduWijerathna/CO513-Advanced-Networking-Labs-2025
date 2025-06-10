from http.server import BaseHTTPRequestHandler, HTTPServer
import requests
import time
import threading

SELECTED_FILE = "/tmp/selected_server"
PORT = 80

# In-memory usage counter
request_count = {
    "172.28.1.11": 0,
    "172.28.1.12": 0
}

class ProxyHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        try:
            # Read selected server IP
            with open(SELECTED_FILE, 'r') as f:
                backend = f.read().strip()

            # Track request count
            if backend in request_count:
                request_count[backend] += 1
            else:
                request_count[backend] = 1  # in case new IP appears

            url = f"http://{backend}{self.path}"

            # Forward request to server
            resp = requests.get(url, timeout=2)

            # Send response headers
            self.send_response(resp.status_code)
            for k, v in resp.headers.items():
                if k.lower() != 'transfer-encoding':
                    self.send_header(k, v)
            self.end_headers()
            
            # Send response content
            try:
                self.wfile.write(resp.content)
            except BrokenPipeError:
                pass

        except Exception as e:
            self.send_response(502)
            self.end_headers()
            try:
                self.wfile.write(f"Error: {e}".encode())
            except BrokenPipeError:
                pass


def log_stats():
    while True:
        time.sleep(5)
        print("\n=== Server Usage Stats ===")
        for server, count in request_count.items():
            print(f"{server}: {count} requests")
        print("===========================\n")


if __name__ == "__main__":
    print(f"Proxy running on port {PORT}...")

    # Start background logging thread
    stats_thread = threading.Thread(target=log_stats, daemon=True)
    stats_thread.start()

    # Start HTTP proxy server
    server = HTTPServer(('', PORT), ProxyHandler)
    server.serve_forever()

