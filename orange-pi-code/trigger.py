import time
import config

_gpio_ready = False


def init():
    global _gpio_ready
    try:
        import OPi.GPIO as GPIO
        GPIO.setmode(GPIO.BOARD)
        GPIO.setup(config.TRIGGER_PIN, GPIO.OUT, initial=GPIO.LOW)
        _gpio_ready = True
    except ImportError:
        print("OPi.GPIO not available — trigger will be simulated (dry run mode)")


def fire():
    if _gpio_ready:
        import OPi.GPIO as GPIO
        GPIO.output(config.TRIGGER_PIN, GPIO.HIGH)
        time.sleep(config.BURST_DURATION)
        GPIO.output(config.TRIGGER_PIN, GPIO.LOW)
    else:
        print(f"[DRY RUN] Trigger fired for {config.BURST_DURATION}s")


def deinit():
    if _gpio_ready:
        import OPi.GPIO as GPIO
        GPIO.output(config.TRIGGER_PIN, GPIO.LOW)
        GPIO.cleanup(config.TRIGGER_PIN)


def in_fire_zone(px, py):
    """Return True if pixel (px, py) falls within the protected garden zone."""
    x_frac = px / config.FRAME_WIDTH
    y_frac = py / config.FRAME_HEIGHT
    return (
        config.FIRE_ZONE_X_MIN <= x_frac <= config.FIRE_ZONE_X_MAX
        and config.FIRE_ZONE_Y_MIN <= y_frac <= config.FIRE_ZONE_Y_MAX
    )
