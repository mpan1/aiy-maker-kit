import json
import socket
import time

DEFAULT_ADDR = ("127.0.0.1", 5005)

class UdpDetectionSender:
    def __init__(self, addr=DEFAULT_ADDR):
        self.addr = addr
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        # Set socket to non-blocking to prevent buffering delays
        self.sock.setblocking(False)
        # Reduce send buffer to prevent kernel buffering
        self.sock.setsockopt(socket.SOL_SOCKET, socket.SO_SNDBUF, 65536)

    def send(self, objects, frame_id):
        msg = {
            "timestamp": time.time(),
            "frame_id": frame_id,
            "objects": objects,
        }
        try:
            self.sock.sendto(json.dumps(msg).encode("utf-8"), self.addr)
        except BlockingIOError:
            # Socket buffer full, drop this packet (expected for real-time streaming)
            pass
