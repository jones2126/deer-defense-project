# System Logic Flowchart

```mermaid
flowchart TD
    A[Start: System Boot] --> B[Initialize Hardware & Software]

    subgraph Initialization
        B --> B1[Load YOLO-World Model<br/>e.g. yolov8l-worldv2]
        B --> B2[Open USB Camera Feed<br/>cv2.VideoCapture(0)]
        B --> B3[Initialize Servos<br/>Pan + Tilt via PWM/PCA9685]
        B --> B4[Initialize Trigger<br/>MOSFET or Relay GPIO]
        B --> B5[Load Configuration<br/>- Target classes: 'deer'<br/>- Confidence threshold<br/>- Cooldown time<br/>- Servo angle limits]
        B --> B6[Camera-to-Servo Calibration<br/>Map pixel coords to servo angles]
    end

    B --> C[Main Control Loop]

    subgraph Real-Time Detection & Targeting Loop
        C --> D[Capture New Frame from Camera]
        D --> E[Preprocess Frame<br/>Resize, normalize if needed]
        E --> F[Run YOLO-World Inference<br/>model.predict(frame, text_prompt='deer')]
        F --> G{Any Detections<br/>with conf > threshold?}
        G -->|No| H[No Target<br/>Optional: Small delay]
        H --> D
        G -->|Yes| I[Select Target<br/>largest / closest / highest confidence]
        I --> J[Calculate Bounding Box Center<br/>x = (x1 + x2)/2<br/>y = (y1 + y2)/2]
        J --> K[Map Pixel Coordinates to Servo Angles]
        K --> L[Apply Smoothing / PID Controller<br/>Optional: Prevent jitter]
        L --> M[Move Servos<br/>pan_servo.angle = calculated_pan<br/>tilt_servo.angle = calculated_tilt]
        M --> N{Target Still Centered?}
        N -->|Yes| O[Fire Water Trigger<br/>GPIO high → MOSFET/Relay ON<br/>Short burst e.g. 500ms]
        N -->|No| P[Re-aim if needed]
        O --> Q[Cooldown Delay<br/>e.g. 2-5 seconds]
        P --> D
        Q --> D
    end

    subgraph Error Handling & Monitoring
        C -.-> R[Monitor System<br/>- Temperature<br/>- FPS / Latency<br/>- Water level optional]
        R -.-> S[Log Detections & Actions<br/>Optional: Send alert]
        S -.-> T[Handle Exceptions<br/>- Camera disconnect<br/>- Servo stall<br/>- Restart loop]
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
