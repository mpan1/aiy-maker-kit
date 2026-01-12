"""
Test UDP detection sender.

This script simulates object detections and sends them over UDP
to whatever receiver is listening (typically the PiCar control code).

Run from the project root as:
    python -m scripts.test_detection_sender
"""

import time
import random

from ipc.udp import UdpDetectionSender


def fake_detections(frame_id: int):
    """
    Generate a fake detection payload for testing.

    Bounding boxes are normalized [0,1].
    """
    # Make the box drift left/right over time so behaviour is visible
    cx = 0.5 + 0.3 * (random.random() - 0.5)
    cy = 0.5
    w = 0.2
    h = 0.3

    xmin = max(0.0, cx - w / 2)
    xmax = min(1.0, cx + w / 2)
    ymin = max(0.0, cy - h / 2)
    ymax = min(1.0, cy + h / 2)

    return [
        {
            "label": "duck",
            "score": round(random.uniform(0.7, 0.95), 2),
            "bbox": [xmin, ymin, xmax, ymax],
        }
    ]


def main():
    sender = UdpDetectionSender()
    frame_id = 0

    print("Starting UDP detection sender")
    print("Sending fake detections to 127.0.0.1:5005")
    print("Press Ctrl+C to stop\n")

    try:
        while True:
            objects = fake_detections(frame_id)
            sender.send(objects, frame_id)

            print(f"Sent frame {frame_id}: {objects}")
            frame_id += 1

            time.sleep(0.1)  # ~10 Hz
    except KeyboardInterrupt:
        print("\nSender stopped.")


if __name__ == "__main__":
    main()