import os

TARGET_CLASS = "deer"           # YOLO-World text prompt
CONFIDENCE_THRESHOLD = 0.5      # Minimum detection confidence to act on
COOLDOWN_SECONDS = 3.0          # Delay between water bursts
BURST_DURATION = 0.5            # Water gun on-time per burst (seconds)

CAMERA_INDEX = 0                # USB camera device index
FRAME_WIDTH = 1920
FRAME_HEIGHT = 1080

# PCA9685 I2C address (default 0x40)
PCA9685_ADDRESS = 0x40

# Servo channel assignments on PCA9685
PAN_CHANNEL = 0
TILT_CHANNEL = 1

# Servo angle limits (degrees)
PAN_MIN = 0
PAN_MAX = 180
PAN_CENTER = 90

TILT_MIN = 30
TILT_MAX = 150
TILT_CENTER = 90

# GPIO pin for water gun trigger (MOSFET gate / relay signal)
TRIGGER_PIN = 18

# Water gun maximum effective range
MAX_WATER_RANGE_FT = 18.0

# Approximate standing deer height — used to estimate range from bounding box size
DEER_HEIGHT_M = 1.2

# AprilTag settings for calibration
APRILTAG_FAMILY = "tag36h11"    # Most common family; print from https://github.com/AprilRobotics/apriltag-imgs
APRILTAG_SIZE_M = 0.15          # Physical width of printed tag in meters (15cm recommended)

# Path to saved calibration file
CALIBRATION_FILE = os.path.join(os.path.dirname(__file__), "calibration.json")

# Fallback static fire zone used when no calibration file exists.
# Fractions of frame width/height — replace with calibrate.py output for accuracy.
FIRE_ZONE_X_MIN = 0.1
FIRE_ZONE_X_MAX = 0.9
FIRE_ZONE_Y_MIN = 0.2
FIRE_ZONE_Y_MAX = 0.9
