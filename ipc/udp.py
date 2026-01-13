import json
import socket
import time
import sys

DEFAULT_ADDR = ("127.0.0.1", 5005)

class UdpDetectionSender:
    def __init__(self, addr=DEFAULT_ADDR):
        self.addr = addr
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        # UDP sender should NOT bind - let OS choose ephemeral port
        # Just ensure socket is ready to send
        self.dropped_count = 0

    def send(self, objects, frame_id):
        msg = {
            "timestamp": time.time(),
            "frame_id": frame_id,
            "objects": objects,
        }
        try:
            self.sock.sendto(json.dumps(msg).encode("utf-8"), self.addr)
            sys.stdout.flush()
        except Exception as e:
            self.dropped_count += 1
            if self.dropped_count % 100 == 1:
                print(f"[WARNING] UDP send error (count={self.dropped_count}): {e}")
                sys.stdout.flush()
