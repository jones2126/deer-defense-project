# Milestones & Deployment Plan

## Getting Started

### Prerequisites

```bash
sudo apt install python3-pip python3-opencv python3-pil git gpiod i2c-tools fswebcam v4l-utils -y
```

### Clone the project

```bash
git clone https://github.com/jones2126/deer-defense-project.git
cd deer-defense-project
```

### Install dependencies

No virtual environment needed — install system-wide (simpler for a dedicated SBC):

```bash
pip3 install -r orange-pi-code/requirements.txt --break-system-packages
```

### Verify Camera

```bash
fswebcam -r 1280x720 --png 0 test.jpg
ls -l test.jpg
```

A working camera produces a file around 2–3 MB. Download via SFTP (e.g. FileZilla, `root@<ip>`) to check image quality. Cheap generic webcams may produce kernel warnings but often still work at lower resolutions.

### Run (CPU/prototype mode)

```bash
python3 orange-pi-code/main.py
```

### Configuration

Edit `orange-pi-code/config.py` to set:
- `TARGET_CLASS` — text prompt for YOLO-World (default: `"deer"`)
- `CONFIDENCE_THRESHOLD` — detection confidence cutoff (default: `0.5`)
- `COOLDOWN_SECONDS` — delay between triggers (default: `3`)
- `BURST_DURATION` — water burst length in seconds (default: `0.5`)
- `TRIGGER_PIN` — GPIO pin number connected to the MOSFET/relay gate (default: `18`)
- `FIRE_ZONE_*` — fractions of the frame defining the protected garden area

---

### OS Image — Setting Up the SD Card

**Recommended OS: Official Orange Pi image (Debian Bookworm server)**

> **Note on the 4GB model:** Armbian Minimal (Trixie/Resolute, vendor kernel) failed to boot
> multiple times — even after fresh flashes with Balena Etcher. This appears to be a known
> issue on some Orange Pi 5 units, particularly the **4GB variant**. The official Orange Pi
> image boots reliably and has full support for USB cameras, GPIO, and the RK3588S chipset.
> Trade-off: slightly higher RAM usage than Armbian minimal, but acceptable for this project.

1. Download the official image from Google Drive:
   https://drive.google.com/drive/folders/1F2uc8v_EQnvsNrevDihwoymOJlFgM-dZ
   Choose `Orangepi5_1.2.2_debian_bookworm_server_linux6.1.99.7z` (or the latest server
   variant) — **server only**, not desktop/Xfce.

2. Flash the image to the 32GB SD card using **Balena Etcher** (recommended, free):
   https://etcher.balena.io/
   - Open Etcher, select the downloaded `.7z` file
   - Select the SD card as the target
   - Click Flash — takes 3–5 minutes

3. Insert the SD card into the Orange Pi 5, connect a monitor and keyboard for first boot.

4. Log in as `root` with password `orangepi` — **change it immediately:**
   ```bash
   passwd
   ```

5. Fix the package sources — the default Huawei mirror is often outdated:
   ```bash
   sudo cp /etc/apt/sources.list /etc/apt/sources.list.backup
   cat <<EOF | sudo tee /etc/apt/sources.list
   deb http://deb.debian.org/debian bookworm main contrib non-free non-free-firmware
   deb http://deb.debian.org/debian bookworm-updates main contrib non-free non-free-firmware
   deb http://deb.debian.org/debian bookworm-backports main contrib non-free non-free-firmware
   deb http://security.debian.org/debian-security bookworm-security main contrib non-free non-free-firmware
   EOF

   sudo rm -f /etc/apt/sources.list.d/docker.list
   ```

6. Update the system:
   ```bash
   sudo apt update && sudo apt upgrade -y
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
1. Flash the **official Orange Pi Bookworm server image** (see OS setup section above)
   — Armbian Minimal failed to boot on the 4GB model; use the official image
2. Fix apt sources (replace Huawei mirror with `deb.debian.org`), then update
3. Install system packages: `python3-pip python3-opencv python3-pil git gpiod i2c-tools fswebcam v4l-utils`
4. Install Python packages system-wide: `pip3 install -r requirements.txt --break-system-packages`
   — No virtualenv needed on a dedicated SBC

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

### Phase 5b: Camera Calibration (1–2 hours)

The camera is mounted in a fixed position separate from the turret. Calibration maps camera pixel coordinates to servo angles and defines the fire zone boundary at your water gun's maximum range (~18 ft).

See the full step-by-step guide: [Camera Calibration Guide](../02-design/camera/calibration-guide.md)

**Quick summary:**
1. Print 8–10 AprilTags (`tag36h11` family) at 15 cm wide
2. Place tags around the garden at varied distances — at least 2 at ~18 ft
3. Run `python3 orange-pi-code/calibrate.py`
4. Aim the turret at each tag with arrow keys, press Space to record
5. Press C to save `calibration.json` (6+ points required)

Re-run calibrate.py any time the camera or turret is repositioned.

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
