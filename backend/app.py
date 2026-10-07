"""In-memory task API for local development."""

import json
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from uuid import uuid4

PORT = 3000
STATUSES = {"todo", "doing", "done"}
tasks = []


class Handler(BaseHTTPRequestHandler):
    def _cors(self):
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "GET, POST, PATCH, DELETE, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "Content-Type")

    def _send(self, status, body=None):
        data = b"" if body is None else json.dumps(body, ensure_ascii=False).encode()
        self.send_response(status)
        self._cors()
        if data:
            self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(data)))
        self.end_headers()
        if data:
            self.wfile.write(data)

    def _read_json(self):
        length = int(self.headers.get("Content-Length", "0"))
        if length == 0:
            return {}
        value = json.loads(self.rfile.read(length).decode())
        if not isinstance(value, dict):
            raise ValueError("object required")
        return value

    def _task_id(self):
        path = self.path.split("?", 1)[0]
        prefix = "/tasks/"
        if not path.startswith(prefix) or "/" in path[len(prefix) :]:
            return None
        return path[len(prefix) :]

    def do_OPTIONS(self):
        self._send(204)

    def do_GET(self):
        if self.path.split("?", 1)[0] != "/tasks":
            self._send(404, {"error": "not found"})
            return
        self._send(200, {"tasks": tasks})

    def do_POST(self):
        if self.path.split("?", 1)[0] != "/tasks":
            self._send(404, {"error": "not found"})
            return
        try:
            body = self._read_json()
        except (json.JSONDecodeError, ValueError, UnicodeDecodeError):
            self._send(400, {"error": "invalid json"})
            return
        title = body.get("title")
        if not isinstance(title, str) or not title.strip():
            self._send(400, {"error": "title is required"})
            return
        task = {"id": str(uuid4()), "title": title.strip(), "status": "todo"}
        tasks.append(task)
        self._send(201, task)

    def do_PATCH(self):
        task_id = self._task_id()
        if task_id is None:
            self._send(404, {"error": "not found"})
            return
        try:
            body = self._read_json()
        except (json.JSONDecodeError, ValueError, UnicodeDecodeError):
            self._send(400, {"error": "invalid json"})
            return
        status = body.get("status")
        if status not in STATUSES:
            self._send(400, {"error": "invalid status"})
            return
        for task in tasks:
            if task["id"] == task_id:
                task["status"] = status
                self._send(200, task)
                return
        self._send(404, {"error": "not found"})

    def do_DELETE(self):
        task_id = self._task_id()
        if task_id is None:
            self._send(404, {"error": "not found"})
            return
        for index, task in enumerate(tasks):
            if task["id"] == task_id:
                tasks.pop(index)
                self._send(204)
                return
        self._send(404, {"error": "not found"})


if __name__ == "__main__":
    server = ThreadingHTTPServer(("127.0.0.1", PORT), Handler)
    print(f"http://127.0.0.1:{PORT}", flush=True)
    server.serve_forever()
