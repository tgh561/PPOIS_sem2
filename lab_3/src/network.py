import json
import socket
import threading
from dataclasses import dataclass
from queue import Queue, Empty


@dataclass
class NetEvent:
    type: str
    data: dict


def _send_json(sock, obj):
    raw = (json.dumps(obj, ensure_ascii=False) + "\n").encode("utf-8")
    sock.sendall(raw)


def _recv_lines(sock, buffer):
    data = sock.recv(4096)
    if not data:
        return None, buffer
    buffer += data.decode("utf-8", errors="ignore")
    lines = []
    while "\n" in buffer:
        line, buffer = buffer.split("\n", 1)
        line = line.strip()
        if line:
            lines.append(line)
    return lines, buffer


class OnlineServer:
    def __init__(self, host="0.0.0.0", port=50007):
        self.host = host
        self.port = port
        self.sock = None
        self.running = False
        self.thread = None
        self.clients = []
        self.names = []
        self.events = Queue()

    def start(self):
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.sock.bind((self.host, self.port))
        self.sock.listen(1)
        self.running = True
        self.thread = threading.Thread(target=self._run, daemon=True)
        self.thread.start()

    def stop(self):
        self.running = False
        try:
            if self.sock:
                self.sock.close()
        except OSError:
            pass
        for c in self.clients:
            try:
                c.close()
            except OSError:
                pass
        self.clients.clear()
        self.names.clear()

    def _run(self):
        try:
            conn, _addr = self.sock.accept()
            self.clients.append(conn)
            self.names.append("Player2")
            self.events.put(NetEvent("client_connected", {"count": len(self.clients)}))

            buffer = ""
            while self.running:
                lines, buffer = _recv_lines(conn, buffer)
                if lines is None:
                    break
                for line in lines:
                    try:
                        msg = json.loads(line)
                    except json.JSONDecodeError:
                        continue
                    self.events.put(NetEvent(msg.get("type", "unknown"), msg))
        except OSError:
            return
        finally:
            self.events.put(NetEvent("disconnected", {}))

    def send_to_client(self, msg):
        if not self.clients:
            return
        try:
            _send_json(self.clients[0], msg)
        except OSError:
            return

    def poll(self):
        out = []
        while True:
            try:
                out.append(self.events.get_nowait())
            except Empty:
                break
        return out


class OnlineClient:
    def __init__(self, host, port=50007):
        self.host = host
        self.port = port
        self.sock = None
        self.running = False
        self.thread = None
        self.events = Queue()

    def connect(self, timeout=3.0):
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.sock.settimeout(timeout)
        self.sock.connect((self.host, self.port))
        self.sock.settimeout(None)
        self.running = True
        self.thread = threading.Thread(target=self._run, daemon=True)
        self.thread.start()

    def close(self):
        self.running = False
        try:
            if self.sock:
                self.sock.close()
        except OSError:
            pass

    def _run(self):
        buffer = ""
        try:
            while self.running:
                lines, buffer = _recv_lines(self.sock, buffer)
                if lines is None:
                    break
                for line in lines:
                    try:
                        msg = json.loads(line)
                    except json.JSONDecodeError:
                        continue
                    self.events.put(NetEvent(msg.get("type", "unknown"), msg))
        except OSError:
            pass
        finally:
            self.events.put(NetEvent("disconnected", {}))

    def send(self, msg):
        if not self.sock:
            return
        try:
            _send_json(self.sock, msg)
        except OSError:
            return

    def poll(self):
        out = []
        while True:
            try:
                out.append(self.events.get_nowait())
            except Empty:
                break
        return out

