# System Logic Flowchart

```mermaid
flowchart TD
    A([Start: System Boot]) --> B[Initialize Hardware and Software]

    subgraph Initialization
        B --> B1[Load YOLO-World Model]
        B --> B2[Open USB Camera Feed]
        B --> B3[Initialize Pan and Tilt Servos]
        B --> B4[Initialize Water Gun Trigger]
        B --> B5[Load Config: target class, confidence, cooldown, angle limits]
        B --> B6[Calibrate Camera-to-Servo Mapping]
    end

    B --> C([Main Control Loop])

    subgraph Detection and Targeting Loop
        C --> D[Capture Frame from Camera]
        D --> E[Preprocess Frame]
        E --> F[Run YOLO-World Inference with prompt: deer]
        F --> G{Detection confidence above threshold?}
        G -->|No| H[No Target - wait]
        H --> D
        G -->|Yes| I[Select Best Target]
        I --> J[Calculate Bounding Box Center]
        J --> K[Map Pixel Coordinates to Servo Angles]
        K --> L[Apply Smoothing or PID]
        L --> M[Move Servos to Aim]
        M --> N{Target centered?}
        N -->|No| P[Re-aim]
        P --> D
        N -->|Yes| O[Fire Water Gun - short burst]
        O --> Q[Cooldown Delay 2 to 5 seconds]
        Q --> D
    end

    subgraph Error Handling and Monitoring
        C -.-> R[Monitor Temp and FPS]
        R -.-> S[Log Detections and Actions]
        S -.-> T[Handle Exceptions and Restart]
    end

    style A fill:#4ade80
    style C fill:#60a5fa
    style G fill:#fbbf24
    style O fill:#f87171
```

## Logic Flow Explanation

1. **Initialization** (runs once at startup)
   - Loads the YOLO-World model (open-vocabulary — change the target text prompt without retraining)
   - Opens the camera and warms it up
   - Sets up servo control (0–180° pan/tilt)
   - Defines how pixel positions map to physical aiming angles (critical calibration step)

2. **Main Loop** (runs continuously, target: 10–30 FPS)
   - **Capture Frame**: Grabs the latest image from the USB camera
   - **Inference**: YOLO-World receives the frame + text prompt (`"deer"`) and returns bounding boxes with confidence scores
   - **Decision**: Only proceed if confidence exceeds threshold (e.g., >0.5) to avoid false sprays
   - **Coordinate Calculation**: Takes the center of the detected bounding box in pixel space

3. **Servo Mapping**
   - Linear mapping example: `pan_angle = (x / frame_width) * 180`
   - More accurate: homography calibration or lookup table
   - Optional PID / exponential smoothing prevents rapid shaking

   ```python
   def pixel_to_servo(x, y, frame_w, frame_h):
       pan  = 90 + (x - frame_w/2) * (90 / (frame_w/2))   # center = 90°
       tilt = 90 + (y - frame_h/2) * (60 / (frame_h/2))   # adjust multipliers
       return clamp(pan, 0, 180), clamp(tilt, 30, 150)     # safety limits
   ```

4. **Actuation**
   - Servos move to the calculated position
   - Once aimed, the trigger GPIO fires for a short burst (enough to scare, not soak)

5. **Cooldown & Loop**
   - Prevents continuous spraying on the same deer (2–5 second delay recommended)
   - Returns to capturing the next frame immediately
