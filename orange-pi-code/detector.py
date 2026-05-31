import config

# Switch BACKEND to "rknn" once the model is converted for the RK3588 NPU.
# Start with "ultralytics" for CPU-based prototyping — no conversion needed.
BACKEND = "ultralytics"


def load_model():
    if BACKEND == "ultralytics":
        from ultralytics import YOLOWorld
        model = YOLOWorld("yolov8l-worldv2.pt")
        model.set_classes([config.TARGET_CLASS])
        return model
    elif BACKEND == "rknn":
        from rknnlite.api import RKNNLite
        model = RKNNLite()
        model.load_rknn("yolo_world_v2l.rknn")
        model.init_runtime()
        return model
    else:
        raise ValueError(f"Unknown backend: {BACKEND}")


def detect(model, frame):
    """Return list of (x1, y1, x2, y2, confidence) for target detections."""
    if BACKEND == "ultralytics":
        results = model.predict(frame, verbose=False)[0]
        detections = []
        for box in results.boxes:
            conf = float(box.conf)
            if conf >= config.CONFIDENCE_THRESHOLD:
                x1, y1, x2, y2 = map(int, box.xyxy[0])
                detections.append((x1, y1, x2, y2, conf))
        return detections
    elif BACKEND == "rknn":
        # Placeholder — replace with your RKNN post-processing logic
        raise NotImplementedError("RKNN inference post-processing not yet implemented")


def best_target(detections):
    """Return the largest detection by bounding box area, or None."""
    if not detections:
        return None
    return max(detections, key=lambda d: (d[2] - d[0]) * (d[3] - d[1]))


def bbox_center(detection):
    x1, y1, x2, y2, _ = detection
    return (x1 + x2) // 2, (y1 + y2) // 2
