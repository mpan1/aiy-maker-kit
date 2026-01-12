from aiymakerkit.utils import send_detections
import time

if __name__ == "__main__":
    frame = 0
    while True:
        # Fake detection for testing
        detections = [
            {
                "label": "duck",
                "score": 0.87,
                "bbox": [0.2, 0.3, 0.5, 0.6]
            }
        ]

        send_detections(detections, frame)
        frame += 1
        time.sleep(0.1)  # ~10 Hz