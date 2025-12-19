import http.server
import socketserver
import webbrowser
import os
import sys

# Configuration
PORT = 8000
DIRECTORY = "."


class Handler(http.server.SimpleHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=DIRECTORY, **kwargs)


def run_server():
    socketserver.TCPServer.allow_reuse_address = True

    with socketserver.TCPServer(("", PORT), Handler) as httpd:
        url = f"http://localhost:{PORT}/public"
        print(f"\n--- VIOLIN ABX EXPERIMENT ---")
        print(f"Server started at: {url}")
        print(f"Serving files from: ./{DIRECTORY}")
        print("Press Ctrl+C to stop the server.\n")

        webbrowser.open(url)

        try:
            httpd.serve_forever()
        except KeyboardInterrupt:
            print("\nServer stopped.")
            sys.exit(0)


if __name__ == "__main__":
    if not os.path.exists(DIRECTORY):
        print(f"Error: Could not find the '{DIRECTORY}' folder.")
        print("Please run this script from the project root.")
    else:
        run_server()
