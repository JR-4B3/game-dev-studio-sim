"""Local browser frontend for the simulation core.

This file is the only place that knows about wall-clock time, HTTP and files.
The core only sees commands, whole days, a seed and a start date.
"""
import argparse
from datetime import date
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
import json
from pathlib import Path
import secrets
import threading
import time
import webbrowser

from core import Game

# Game days per real second for speeds 0 (paused) to 3.
SPEEDS = (0.0, 0.7, 1.4, 2.8)
WEB = Path(__file__).parent / "web"
TYPES = {".html": "text/html", ".js": "text/javascript", ".css": "text/css", ".woff2": "font/woff2"}


class Session:
    """One running game plus the real-time clock that drives it."""

    def __init__(self, save_path):
        self.save_path = Path(save_path)
        self.game = None
        self.speed = 0
        self.resume_speed = 1
        self.carry = 0.0
        self.last_tick = time.monotonic()
        self.last_contact = self.last_tick
        self.lock = threading.Lock()

    def tick(self):
        with self.lock:
            now = time.monotonic()
            elapsed = min(now - self.last_tick, 0.5)
            self.last_tick = now
            # Time only runs while a browser tab is actually watching.
            if not self.game or not self.speed or now - self.last_contact > 3:
                self.carry = 0.0
                return
            self.carry += elapsed * SPEEDS[self.speed]
            while self.carry >= 1 and not self.game.blocked():
                self.carry -= 1
                self.game.advance_days(1)
                if self.game.s.ironman and (self.game.date.weekday() == 6 or self.game.blocked()):
                    self.save()
            if self.game.blocked():
                self.carry = 0.0

    def save(self):
        self.save_path.parent.mkdir(parents=True, exist_ok=True)
        temp = self.save_path.with_suffix(".tmp")
        temp.write_text(json.dumps(self.game.to_save()))
        temp.replace(self.save_path)

    def view(self):
        if self.game is None:
            return {"started": False, "can_load": self.save_path.is_file()}
        return {**self.game.view(), "started": True, "can_load": self.save_path.is_file(),
                "clock": {"speed": self.speed, "fraction": self.carry,
                          "days_per_second": SPEEDS[self.speed],
                          "held": self.game.blocked()}}

    def handle(self, data):
        action = data.get("action")
        if action == "new":
            seed = data.get("seed")
            ironman = data.get("ironman") is True
            self.game = Game.new(seed if type(seed) is int else secrets.randbelow(2**31), date.today(), ironman=ironman)
            self.speed, self.resume_speed = 0, 1
            if ironman:
                self.save()
        elif action == "load":
            self.game = Game.from_save(json.loads(self.save_path.read_text()))
            self.speed = 0
        elif self.game is None:
            raise ValueError("Start or load a studio first.")
        elif action == "save":
            if self.game.s.ironman:
                raise ValueError("Ironman studios save themselves every week.")
            self.save()
            self.game.log("Studio saved.")
        elif action == "pause":
            if self.speed:
                self.resume_speed, self.speed = self.speed, 0
            else:
                self.speed = self.resume_speed
        elif action == "speed":
            index = data.get("index")
            if type(index) is not int or not 0 <= index < len(SPEEDS):
                raise ValueError("Invalid speed.")
            self.speed = index
            if index:
                self.resume_speed = index
        else:
            self.game.command(data)
            if self.game.s.ironman:
                self.save()


def serve(port, save_path, open_browser):
    session = Session(save_path)
    token = secrets.token_urlsafe(24)

    class Handler(BaseHTTPRequestHandler):
        def send(self, body, kind="application/json", status=200):
            self.send_response(status)
            self.send_header("Content-Type", kind + "; charset=utf-8")
            self.send_header("Content-Length", str(len(body)))
            self.send_header("Cache-Control", "no-store")
            self.send_header("Content-Security-Policy", "default-src 'self'; style-src 'self' 'unsafe-inline'; frame-ancestors 'none'")
            self.end_headers()
            self.wfile.write(body)

        def state(self):
            session.last_contact = time.monotonic()
            with session.lock:
                return json.dumps({**session.view(), "token": token}).encode()

        def do_GET(self):
            if self.path == "/api/state":
                return self.send(self.state())
            name = "index.html" if self.path == "/" else self.path.lstrip("/")
            target = (WEB / name).resolve()
            if WEB.resolve() in target.parents and target.is_file() and target.suffix in TYPES:
                return self.send(target.read_bytes(), TYPES[target.suffix])
            self.send(b"{}", status=404)

        def do_POST(self):
            if self.path != "/api/action" or self.headers.get("X-Game-Token") != token:
                return self.send(b"{}", status=403)
            try:
                size = int(self.headers.get("Content-Length", 0))
                if not 0 < size <= 8192:
                    raise ValueError("Invalid request size.")
                data = json.loads(self.rfile.read(size))
                if not isinstance(data, dict):
                    raise ValueError("Expected an action object.")
                with session.lock:
                    session.handle(data)
                self.send(self.state())
            except (ValueError, KeyError, IndexError, TypeError, OSError) as error:
                self.send(json.dumps({"error": str(error)}).encode(), status=400)

        def log_message(self, *args):
            pass

    server = ThreadingHTTPServer(("127.0.0.1", port), Handler)
    stop = threading.Event()

    def clock():
        while not stop.wait(0.05):
            session.tick()

    threading.Thread(target=clock, daemon=True).start()
    url = f"http://127.0.0.1:{server.server_port}"
    print(f"Game Dev Studio Sim is running at {url}\nPress Ctrl+C to stop. Save in the game before closing.")
    if open_browser:
        webbrowser.open(url)
    try:
        server.serve_forever(poll_interval=0.2)
    except KeyboardInterrupt:
        pass
    finally:
        stop.set()
        server.server_close()


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--port", type=int, default=8765)
    parser.add_argument("--save-file", default="saves/studio.json")
    parser.add_argument("--no-browser", action="store_true")
    args = parser.parse_args()
    serve(args.port, args.save_file, not args.no_browser)
