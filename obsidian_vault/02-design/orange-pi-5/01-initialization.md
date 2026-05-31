# Initialization

Runs once at system boot before the main loop starts.

```mermaid
flowchart TD
    A([System Boot]) --> B[Load YOLO-World Model]
    B --> C[Open USB Camera Feed]
    C --> D[Initialize Pan and Tilt Servos]
    D --> E[Initialize Water Gun Trigger]
    E --> F[Load Configuration File]
    F --> G[Run Camera-to-Servo Calibration]
    G --> H([Enter Main Loop])

    style A fill:#4ade80
    style H fill:#60a5fa
```

## Notes

- **Model**: `yolov8l-worldv2` — open-vocabulary, so the target text prompt can be changed without retraining
- **Config values loaded**: target class, confidence threshold, cooldown duration, servo angle limits
- **Calibration**: maps pixel coordinates (e.g. 1920×1080) to servo angles (0–180°) — most important tuning step
- If any step fails, the system should log the error and halt rather than run uncalibrated

[Back to Overview](overview.md)
