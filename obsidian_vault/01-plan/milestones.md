# Milestones & Deployment Plan

## Getting Started

### Prerequisites

```bash
sudo apt update && sudo apt install python3 python3-pip python3-venv git -y
```

### Install dependencies

```bash
python3 -m venv venv
source venv/bin/activate
pip install -r orange-pi-code/requirements.txt
```

### Run (CPU/prototype mode)

```bash
python3 orange-pi-code/main.py
```

### Configuration

Edit `src/config.py` to set:
- `TARGET_CLASS` — text prompt for YOLO-World (default: `"deer"`)
- `CONFIDENCE_THRESHOLD` — detection confidence cutoff (default: `0.5`)
- `COOLDOWN_SECONDS` — delay between triggers (default: `3`)
- `BURST_DURATION` — water burst length in seconds (default: `0.5`)

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

See [Orange Pi 5 Overview](../02-design/orange-pi-5/overview.md) for the detection loop code and implementation notes.

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
- Daytime vs low-light performance (Arducam handles this automatically via IR-cut)
- Servo speed and aiming accuracy
- Water pressure and range of the water gun
- False positive rate — tune confidence threshold or add size filtering (deer are large)
- Power consumption for 24/7 operation
- **Advanced ideas**: solar panel + battery, web UI for live target-class config, multiple zones covering the whole garden
