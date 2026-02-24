"""Flask web server for viewing miner scan results."""

import threading
from flask import Flask, render_template, redirect, url_for, jsonify

app = Flask(__name__)


class SharedState:
    """Thread-safe shared state between GUI and web server."""

    def __init__(self) -> None:
        self._lock = threading.Lock()
        self.miners: list[dict] = []
        self.last_scan: str | None = None
        self.scanning = False
        self.scan_requested = False

    def get_snapshot(self) -> tuple[list[dict], str | None, bool]:
        with self._lock:
            return (list(self.miners), self.last_scan, self.scanning)

    def set_miners(self, miners: list[dict]) -> None:
        with self._lock:
            self.miners = miners

    def set_last_scan(self, when: str | None) -> None:
        with self._lock:
            self.last_scan = when

    def set_scanning(self, scanning: bool) -> None:
        with self._lock:
            self.scanning = scanning

    def request_scan(self) -> bool:
        with self._lock:
            if self.scanning:
                return False
            self.scan_requested = True
            return True

    def consume_scan_request(self) -> bool:
        with self._lock:
            if self.scan_requested:
                self.scan_requested = False
                return True
            return False

    def clear_scan_request(self) -> None:
        with self._lock:
            self.scan_requested = False


def create_app(shared_state: SharedState) -> Flask:
    """Create Flask app with routes bound to shared state."""

    @app.route("/")
    def index() -> str:
        miners, last_scan, scanning = shared_state.get_snapshot()
        return render_template("index.html", miners=miners, last_scan=last_scan, scanning=scanning)

    @app.route("/api/miners")
    def api_miners() -> tuple:
        miners, last_scan, scanning = shared_state.get_snapshot()

        def _serialize(m: dict) -> dict:
            m2 = dict(m)
            workers = m2.get("workers") or []
            m2["workers"] = [{"url": u, "user": ur} for u, ur in workers]
            return m2

        return jsonify({
            "miners": [_serialize(m) for m in miners],
            "last_scan": last_scan,
            "scanning": scanning,
        })

    @app.route("/scan", methods=["POST"])
    def trigger_scan() -> tuple:
        if shared_state.request_scan():
            return redirect(url_for("index"), code=302)
        return redirect(url_for("index"), code=302)

    return app


def run_server(shared_state: SharedState, host: str = "0.0.0.0", port: int = 80) -> None:
    """Run Flask server in a daemon thread."""
    flask_app = create_app(shared_state)
    flask_app.run(host=host, port=port, threaded=True, use_reloader=False)
