import http.server
import socketserver
import mimetypes
import webbrowser
import json
import re
from pathlib import Path

PORT = 8000
ROOT = Path(__file__).resolve().parent

mimetypes.add_type("application/json", ".json")
mimetypes.add_type("application/geo+json", ".geojson")
mimetypes.add_type("image/png", ".png")

def next_numeric_filename(directory: Path) -> str:
    nums = []
    for p in directory.iterdir():
        if p.is_file() and re.fullmatch(r"\d+", p.name):
            try:
                nums.append(int(p.name))
            except ValueError:
                pass
    return str((max(nums) if nums else 0) + 1)

class Handler(http.server.SimpleHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=str(ROOT), **kwargs)

    def end_headers(self):
        self.send_header("Cache-Control", "no-store")
        super().end_headers()

    def do_POST(self):
        if self.path != "/save":
            self.send_response(404)
            self.send_header("Content-Type", "application/json; charset=utf-8")
            self.end_headers()
            self.wfile.write(json.dumps({"ok": False, "error": "Not Found"}, ensure_ascii=False).encode("utf-8"))
            return

        length = int(self.headers.get("Content-Length", "0"))
        if length <= 0 or length > 10_000_000:
            self.send_response(400)
            self.send_header("Content-Type", "application/json; charset=utf-8")
            self.end_headers()
            self.wfile.write(json.dumps({"ok": False, "error": "Invalid Content-Length"}, ensure_ascii=False).encode("utf-8"))
            return

        raw = self.rfile.read(length)
        try:
            data = json.loads(raw.decode("utf-8"))
        except Exception as ex:
            self.send_response(400)
            self.send_header("Content-Type", "application/json; charset=utf-8")
            self.end_headers()
            self.wfile.write(json.dumps({"ok": False, "error": f"Invalid JSON: {ex}"}, ensure_ascii=False).encode("utf-8"))
            return

        filename = next_numeric_filename(ROOT)  # "1", "2", "3", ...
        (ROOT / filename).write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")

        self.send_response(200)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.end_headers()
        self.wfile.write(json.dumps({"ok": True, "file": filename}, ensure_ascii=False).encode("utf-8"))

if __name__ == "__main__":
    with socketserver.ThreadingTCPServer(("127.0.0.1", PORT), Handler) as httpd:
        url = f"http://127.0.0.1:{PORT}/index.html"
        print(f"Serving: {url}")
        webbrowser.open(url)
        httpd.serve_forever()
