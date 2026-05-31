# Deer Defense System — Automated Water Gun Turret for Tomato Plants

An AI-powered, automated water gun turret that detects deer using computer vision and fires a water burst to deter them from your tomato plants.

---

## Project Overview

- **Goal**: Protect tomato plants from deer using a humane, automated water deterrent.
- **Detection**: YOLO-World v2 (open-vocabulary) — detects "deer" (or any text prompt: rabbit, groundhog, etc.)
- **Hardware**: Orange Pi 5 (RK3588 NPU) + USB camera + 2 servos + disassembled electric water gun
- **Inference**: Runs fully local/on-device, 24/7, no cloud needed
- **Inspired by**: u/muxamilian's automated pigeon defense system (r/SideProject, April 2026)

---

## Bill of Materials (BOM)

**Estimated total cost**: $150–350 USD

### 1. Computing & Vision
- **Orange Pi 5** (or 5 Plus/Pro) — RK3588 NPU (6 TOPS)
- 5V/4A+ USB-C or barrel power supply (PoE hat optional)
- **USB Camera** — Logitech C920/C270 or generic wide-angle 1080p (UVC-compatible)
- SD card (32GB+ Class 10/A2) or eMMC module

### 2. Actuation (Aiming)
- **2× Servo motors**: MG90S or MG996R (metal gear recommended for outdoor use)
- Pan-tilt bracket / servo mount kit (or 3D-print from Thingiverse/Printables)
- Optional: **PCA9685** 16-channel PWM servo driver (I²C) — reduces jitter, frees GPIO pins

### 3. Water Gun & Triggering
- **Battery-powered electric water gun** (cheap toy) — disassemble to access pump circuit
- **IRLZ44N** N-channel logic-level MOSFET + resistors (10kΩ pull-down, ~220Ω gate resistor)
- Alternative: 5V relay module (simpler/safer isolation)
- Jumper wires, breadboard/perfboard, Dupont connectors, heat shrink

### 4. Mechanical & Mounting
- 3D-printed or custom turret mount (holds camera + servos + water gun)
- Base/platform (wood, acrylic, or repurposed mount)
- Weatherproof enclosure for Orange Pi + electronics (IP-rated if possible)
- Cable management, zip ties, hot glue/epoxy, screws, silicone sealant

### 5. Power & Misc
- Separate 5V/6V battery pack or regulated supply for servos + water gun pump
- Do **not** power servos from the Orange Pi 5V rail under load
- Multimeter, soldering iron, wire strippers
- Optional: Small fan + heatsink for Orange Pi under sustained NPU load

**Rough cost breakdown**:
- Orange Pi 5 + PSU + camera: ~$80–120
- Servos + mounts + water gun: ~$30–60
- Electronics/misc: ~$20–40
- Enclosure/3D printing: variable

---

## System Logic Flow

```mermaid
flowchart TD
    A[Start: System Boot] --> B[Initialize Hardware & Software]

    subgraph Initialization
        B --> B1[Load YOLO-World Model<br/>e.g. yolov8l-worldv2]
        B --> B2[Open USB Camera Feed<br/>cv2.VideoCapture(0)]
        B --> B3[Initialize Servos<br/>Pan + Tilt via PWM/PCA9685]
        B --> B4[Initialize Trigger<br/>MOSFET or Relay GPIO]
        B --> B5[Load Configuration<br/>- Target classes: ['deer']<br/>- Confidence threshold<br/>- Cooldown time<br/>- Servo angle limits]
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

---

## Step-by-Step Development Plan

### Phase 1: Planning & Mechanical Design (1–2 days)
1. Decide mounting location (garden stake, fence post, raised bed corner, etc.)
2. Design or buy a **pan-tilt mechanism** that holds the water gun + camera rigidly
3. Disassemble the water gun — identify how to trigger the pump (MOSFET vs relay)
4. Sketch wiring diagram and plan power rails
5. Plan coverage zone: map out where deer approach the tomato plants

**Tip**: 3D print a pan-tilt turret — many STL files on Thingiverse/Printables.

### Phase 2: Electronics Assembly & Basic Control (2–4 days)
1. Wire the two servos (signal, power, ground). Test with simple Python PWM first.
2. Build the trigger circuit:
   - MOSFET version: GPIO → Gate drives Drain/Source to switch water gun pump
   - Relay version: simpler, safer isolation
3. Connect USB camera and verify it works (`lsusb`, `fswebcam`, or OpenCV test)
4. Test basic movement + trigger without AI

**Recommended libraries**: `OPi.GPIO` or `gpiod` for GPIO; `adafruit-circuitpython-pca9685` if using the PWM driver.

### Phase 3: Software Environment Setup on Orange Pi 5 (1–2 days)
1. Flash **Armbian** (recommended for RK3588) or official Orange Pi OS
2. Update system, install: `python3`, `pip`, `git`, `opencv-python`, `numpy`
3. Install GPIO libraries and test
4. Set up a Python virtual environment

### Phase 4: AI Model — YOLO-World Inference (3–7 days)

Uses **yolo_world_v2l** (open-vocabulary — change target text without retraining).

**Options**:
- **Easiest starting point**: Ultralytics YOLO-World → export to ONNX, run on CPU first
- **Full NPU acceleration**: Convert to **RKNN** format using `rknn-toolkit2`
  - Export model to ONNX → convert with Rockchip tools → run on RK3588 NPU

**Basic detection loop** (Python pseudocode):
```python
import cv2

model = load_yolo_world("yolo_world_v2l.rknn")  # or ONNX for initial dev

cap = cv2.VideoCapture(0)

while True:
    ret, frame = cap.read()
    results = model.infer(frame, text_prompt="deer")

    for det in results:
        if det.conf > 0.5:
            x_center, y_center = get_bbox_center(det)
            aim_servos(x_center, y_center)
            trigger_water_gun(duration=0.5)  # short burst
            time.sleep(2)  # cooldown
```

**Pixel-to-servo mapping**:
```python
def pixel_to_servo(x, y, frame_w, frame_h):
    pan  = 90 + (x - frame_w/2) * (90 / (frame_w/2))   # center = 90°
    tilt = 90 + (y - frame_h/2) * (60 / (frame_h/2))   # adjust multipliers
    return clamp(pan, 0, 180), clamp(tilt, 30, 150)     # safety limits
```

**Calibration**: Map camera FOV + resolution to servo angle ranges. Start with printed targets before deploying outdoors.

Start with **CPU/OpenCV + Ultralytics** for rapid prototyping, then move to NPU.

### Phase 5: Full Integration & Logic (3–5 days)
1. Combine detection + servo control + trigger
2. Add logic:
   - Only trigger if target is inside the "garden zone" (bounding box region of frame)
   - Short bursts + cooldown to avoid wasting water
   - Optional: logging, Telegram/email alert on detection, web dashboard
3. Handle edge cases: multiple deer, false positives, low light, night detection
4. Add config file for target class (`"deer"`, `"rabbit"`, `"groundhog"`, etc.)

### Phase 6: Enclosure, Weatherproofing & Installation (2–4 days)
1. Mount everything securely near the tomato bed
2. Waterproof electronics (conformal coating, sealed enclosure, desiccant)
3. Route cables safely, protect from rain
4. Long-term outdoor testing
5. Add systemd service + watchdog for auto-restart

### Phase 7: Testing, Tuning & Improvements
- Daytime vs low-light performance (add IR camera for night coverage)
- Servo speed and aiming accuracy
- Water pressure and range of the toy gun
- False positive rate — tune confidence threshold or add size filtering (deer are large)
- Power consumption for 24/7 operation
- **Advanced ideas**: solar panel + battery, IR night vision, web UI for live target-class config, multiple zones covering the whole garden

---

## Key Implementation Notes

- **Performance**: Orange Pi 5 + RK3588 NPU can achieve real-time tracking (10–30 FPS)
- **Target prompt**: Use `"deer"` as the YOLO-World text prompt; also try `"white-tailed deer"` for better accuracy
- **Fire zone restriction**: Only spray when the bounding box center falls within a defined pixel region (the garden rows), reducing false triggers on passing animals outside the protected area
- **Cooldown**: 2–5 seconds recommended for deer (longer than pigeons — deer take more convincing)
- **Multi-target**: Track the largest detection (deer are big) or highest-confidence one

---

## Resources
- YOLO-World official: https://github.com/AILab-CVC/YOLO-World
- Ultralytics YOLO-World docs (easier starting point for prototyping)
- Rockchip RKNN examples + Ultralytics RKNN export guide
- Thingiverse/Printables: search "pan tilt servo turret"
- Inspiration: [u/muxamilian's pigeon defense system](https://www.reddit.com/r/SideProject/comments/1s9ywir/automated_pigeon_defense_system/)
