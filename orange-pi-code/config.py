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

# Fire zone: fraction of frame that defines the protected garden area
# Only spray when target center falls within this region
FIRE_ZONE_X_MIN = 0.1           # 10% from left edge
FIRE_ZONE_X_MAX = 0.9           # 10% from right edge
FIRE_ZONE_Y_MIN = 0.2           # 20% from top
FIRE_ZONE_Y_MAX = 0.9           # 10% from bottom
