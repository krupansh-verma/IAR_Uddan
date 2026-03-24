import http.server
import socketserver
import webbrowser
import threading
import os
import sys

# We force 127.0.0.1 (localhost) because browsers only allow Microphone access on secure contexts (HTTPS) or localhost.
# If you run on a generic IP like 192.168.x.x without HTTPS, the mic will be permanently blocked by Chrome/Edge.
HOST = "127.0.0.1"
PORT = 8000
DIRECTORY = os.path.dirname(os.path.abspath(__file__))

class Handler(http.server.SimpleHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=DIRECTORY, **kwargs)

def start_server():
    with socketserver.TCPServer((HOST, PORT), Handler) as httpd:
        print(f"✅ Serving PolicyPilot at http://{HOST}:{PORT}")
        httpd.serve_forever()

if __name__ == '__main__':
    print("Starting local Web Server to enable Microphone API...")
    server_thread = threading.Thread(target=start_server, daemon=True)
    server_thread.start()
    
    url = f"http://{HOST}:{PORT}/standalone_react.html"
    print(f"🌐 Automatically opening browser to: {url}")
    
    # Open the browser automatically
    webbrowser.open(url)
    
    print("\nPress Ctrl+C to stop the server.")
    try:
        while True:
            server_thread.join(1)
    except KeyboardInterrupt:
        print("\nShutting down server.")
        sys.exit(0)
