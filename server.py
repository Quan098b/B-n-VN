import http.server
import socketserver
import mimetypes
import webbrowser
from pathlib import Path

PORT = 8000
ROOT = Path(__file__).resolve().parent

# MIME cho GeoJSON (ổn định hơn khi fetch)
mimetypes.add_type("application/geo+json", ".geojson")
mimetypes.add_type("application/json", ".json")

class Handler(http.server.SimpleHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=str(ROOT), **kwargs)

    def end_headers(self):
        self.send_header("Cache-Control", "no-store")
        super().end_headers()

with socketserver.TCPServer(("127.0.0.1", PORT), Handler) as httpd:
    url = f"http://127.0.0.1:{PORT}/index.html"
    print(f"Serving: {url}")
    webbrowser.open(url)
    httpd.serve_forever()
