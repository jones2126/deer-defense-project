import time
import json
import logging
import cv2

import config
import detector
import servo_control
import trigger

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
)
log = logging.getLogger(__name__)


def load_calibration_data():
    """Load fire zone polygon and min bbox height from calibration file."""
    try:
        with open(config.CALIBRATION_FILE) as f:
            data = json.load(f)
        polygon = data.get("fire_zone_polygon")
        min_bbox_height = data.get("min_deer_bbox_height", 0)
        log.info("Calibration loaded — fire zone polygon: %d points, min bbox height: %d px",
                 len(polygon) if polygon else 0, min_bbox_height)
        return polygon, min_bbox_height
    except FileNotFoundError:
        log.warning("No calibration file found — using static fire zone from config. "
                    "Run calibrate.py for accurate range limiting.")
        return None, 0


def bbox_height(detection):
    _, y1, _, y2, _ = detection
    return y2 - y1


def init_camera():
    cap = cv2.VideoCapture(config.CAMERA_INDEX)
    cap.set(cv2.CAP_PROP_FRAME_WIDTH, config.FRAME_WIDTH)
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, config.FRAME_HEIGHT)
    if not cap.isOpened():
        raise RuntimeError("Could not open camera")
    log.info("Camera opened: %dx%d", config.FRAME_WIDTH, config.FRAME_HEIGHT)
    return cap


def reconnect_camera(cap):
    cap.release()
    time.sleep(2)
    return init_camera()


def run():
    log.info("Loading model...")
    model = detector.load_model()
    log.info("Model loaded")

    log.info("Initializing servos...")
    servo_control.init()
    calibrated = servo_control.load_calibration()
    if not calibrated:
        log.warning("Servo calibration not found — using linear pixel-to-angle mapping. "
                    "Run calibrate.py for fixed-camera accuracy.")

    log.info("Initializing trigger...")
    trigger.init()

    fire_zone_polygon, min_bbox_height = load_calibration_data()

    cap = init_camera()
    last_fire_time = 0.0

    log.info("Entering main loop — watching for %s", config.TARGET_CLASS)

    try:
        while True:
            ret, frame = cap.read()
            if not ret:
                log.warning("Frame read failed — attempting camera reconnect")
                cap = reconnect_camera(cap)
                continue

            detections = detector.detect(model, frame)
            target = detector.best_target(detections)

            if target is None:
                continue

            px, py = detector.bbox_center(target)
            servo_control.aim_at_pixel(px, py)

            # Range check: deer bounding box must be tall enough to be within
            # water gun range. Calibrate.py sets min_bbox_height based on the
            # tag placed at MAX_WATER_RANGE_FT during calibration.
            if min_bbox_height > 0 and bbox_height(target) < min_bbox_height:
                log.debug("Deer too far (bbox height %dpx < %dpx) — skipping fire",
                          bbox_height(target), min_bbox_height)
                continue

            now = time.time()
            if (
                now - last_fire_time >= config.COOLDOWN_SECONDS
                and trigger.in_fire_zone(px, py, polygon=fire_zone_polygon)
            ):
                log.info("Deer in range at (%d, %d) conf=%.2f bbox_h=%dpx — firing",
                         px, py, target[4], bbox_height(target))
                trigger.fire()
                last_fire_time = now

    except KeyboardInterrupt:
        log.info("Stopped by user")
    finally:
        cap.release()
        servo_control.deinit()
        trigger.deinit()
        log.info("Shutdown complete")


if __name__ == "__main__":
    run()
