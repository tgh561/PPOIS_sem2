import json
import socket
import threading
import time
from dataclasses import dataclass


@dataclass
class HostInfo:
    name: str
    ip: str
    port: int
    last_seen: float


def _local_ip_guess():
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))
        ip = s.getsockname()[0]
        s.close()
        return ip
    except OSError:
        return "127.0.0.1"


class HostBroadcaster:
    def __init__(self, name, tcp_port, discovery_port, interval_ms=700):
        self.name = name
        self.tcp_port = tcp_port
        self.discovery_port = discovery_port
        self.interval_ms = interval_ms
        self.running = False
        self.thread = None
        self.ip = _local_ip_guess()

    def start(self):
        if self.running:
            return
        self.running = True
        self.thread = threading.Thread(target=self._run, daemon=True)
        self.thread.start()

    def stop(self):
        self.running = False

    def _run(self):
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        sock.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
        while self.running:
            msg = {
                "type": "reversi_host",
                "name": self.name,
                "ip": self.ip,
                "port": self.tcp_port,
                "time": time.time(),
            }
            data = (json.dumps(msg, ensure_ascii=False) + "\n").encode("utf-8")
            try:
                sock.sendto(data, ("255.255.255.255", self.discovery_port))
            except OSError:
                pass
            time.sleep(self.interval_ms / 1000.0)


class HostListener:
    def __init__(self, discovery_port):
        self.discovery_port = discovery_port
        self.running = False
        self.thread = None
        self.hosts = {}

    def start(self):
        if self.running:
            return
        self.running = True
        self.thread = threading.Thread(target=self._run, daemon=True)
        self.thread.start()

    def stop(self):
        self.running = False

    def _run(self):
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        try:
            sock.bind(("", self.discovery_port))
        except OSError:
            return

        while self.running:
            try:
                data, addr = sock.recvfrom(4096)
            except OSError:
                break
            try:
                msg = json.loads(data.decode("utf-8", errors="ignore").strip())
            except json.JSONDecodeError:
                continue
            if msg.get("type") != "reversi_host":
                continue
            name = msg.get("name", "Host")
            ip = msg.get("ip") or addr[0]
            port = int(msg.get("port", 50007))
            key = f"{ip}:{port}"
            self.hosts[key] = HostInfo(name=name, ip=ip, port=port, last_seen=time.time())

    def get_hosts(self, ttl_seconds=2.5):
        now = time.time()
        alive = []
        for key, info in list(self.hosts.items()):
            if now - info.last_seen <= ttl_seconds:
                alive.append(info)
            else:
                del self.hosts[key]
        alive.sort(key=lambda h: (h.name.lower(), h.ip, h.port))
        return alive

