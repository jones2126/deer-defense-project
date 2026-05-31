import json
import numpy as np
import config

# Smoothing factor: 0.0 = instant snap, 1.0 = never moves.
SMOOTHING = 0.4

_pan_angle = float(config.PAN_CENTER)
_tilt_angle = float(config.TILT_CENTER)
_pca = None
_homography = None      # Set by load_calibration(); None = use linear fallback


def init():
    global _pca
    from adafruit_pca9685 import PCA9685
    import board
    import busio
    i2c = busio.I2C(board.SCL, board.SDA)
    _pca = PCA9685(i2c, address=config.PCA9685_ADDRESS)
    _pca.frequency = 50
    move_to(config.PAN_CENTER, config.TILT_CENTER)


def load_calibration(path=None):
    """Load homography matrix from calibration.json. Returns True on success."""
    global _homography
    path = path or config.CALIBRATION_FILE
    try:
        with open(path) as f:
            data = json.load(f)
        _homography = np.array(data["homography"], dtype=np.float64)
        return True
    except (FileNotFoundError, KeyError):
        return False


def get_angles():
    """Return current (pan, tilt) angles in degrees."""
    return _pan_angle, _tilt_angle


def _clamp(value, lo, hi):
    return max(lo, min(hi, value))


def _angle_to_duty(angle):
    # Maps 0–180° to PCA9685 12-bit duty cycle for a standard servo
    # (1ms–2ms pulse width within a 20ms period at 50Hz)
    min_duty = 1638   # ~1ms
    max_duty = 8192   # ~2ms
    return int(min_duty + (angle / 180.0) * (max_duty - min_duty))


def move_to(pan, tilt):
    global _pan_angle, _tilt_angle
    pan = _clamp(pan, config.PAN_MIN, config.PAN_MAX)
    tilt = _clamp(tilt, config.TILT_MIN, config.TILT_MAX)
    _pan_angle = pan
    _tilt_angle = tilt
    if _pca:
        _pca.channels[config.PAN_CHANNEL].duty_cycle = _angle_to_duty(pan)
        _pca.channels[config.TILT_CHANNEL].duty_cycle = _angle_to_duty(tilt)


def aim_at_pixel(px, py):
    """Move servos to point at camera pixel (px, py).

    Uses calibration homography when available; falls back to linear mapping
    when no calibration file has been loaded (e.g. during initial setup).
    """
    if _homography is not None:
        src = np.array([[[float(px), float(py)]]], dtype=np.float64)
        dst = cv2.perspectiveTransform(src, _homography)
        pan_target, tilt_target = dst[0][0]
    else:
        pan_target = config.PAN_CENTER + (px - config.FRAME_WIDTH / 2) * (
            (config.PAN_MAX - config.PAN_MIN) / config.FRAME_WIDTH
        )
        tilt_target = config.TILT_CENTER + (py - config.FRAME_HEIGHT / 2) * (
            (config.TILT_MAX - config.TILT_MIN) / config.FRAME_HEIGHT
        )

    new_pan  = _pan_angle  + (1 - SMOOTHING) * (pan_target  - _pan_angle)
    new_tilt = _tilt_angle + (1 - SMOOTHING) * (tilt_target - _tilt_angle)
    move_to(new_pan, new_tilt)


def center():
    move_to(config.PAN_CENTER, config.TILT_CENTER)


def deinit():
    if _pca:
        center()
        _pca.deinit()


# cv2 imported here to avoid a hard dependency at module load time on systems
# where OpenCV is not yet installed (e.g. during pip install).
try:
    import cv2
except ImportError:
    cv2 = None
