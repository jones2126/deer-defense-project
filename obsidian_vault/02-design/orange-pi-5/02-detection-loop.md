# Detection and Targeting Loop

Runs continuously at 10–30 FPS after initialization.

```mermaid
flowchart TD
    A([Start of Loop]) --> B[Capture Frame from Camera]
    B --> C[Preprocess Frame]
    C --> D[Run YOLO-World Inference]
    D --> E{Confidence above threshold?}
    E -->|No| A
    E -->|Yes| F[Select Best Target]
    F --> G[Calculate Bounding Box Center]
    G --> H[Map Pixels to Servo Angles]
    H --> I[Apply Smoothing or PID]
    I --> J[Move Servos to Aim]
    J --> K{Target Centered?}
    K -->|No| B
    K -->|Yes| L[Fire Water Gun]
    L --> M[Cooldown Delay]
    M --> A

    style A fill:#60a5fa
    style E fill:#fbbf24
    style K fill:#fbbf24
    style L fill:#f87171
```

## Notes

- **YOLO-World text prompt**: `"deer"` — also try `"white-tailed deer"` for higher accuracy
- **Confidence threshold**: 0.5 recommended; lower = more triggers, higher = fewer false positives
- **Target selection**: pick the largest bounding box (deer are big) or highest confidence detection
- **Pixel-to-servo mapping**:
  ```python
  def pixel_to_servo(x, y, frame_w, frame_h):
      pan  = 90 + (x - frame_w/2) * (90 / (frame_w/2))
      tilt = 90 + (y - frame_h/2) * (60 / (frame_h/2))
      return clamp(pan, 0, 180), clamp(tilt, 30, 150)
  ```
- **Fire zone**: only trigger if the bounding box center falls within a defined region of the frame (the garden area), ignoring deer passing outside the protected zone
- **Cooldown**: 2–5 seconds — deer need more convincing than birds

[Back to Overview](overview.md)
