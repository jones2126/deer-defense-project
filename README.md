# Deer Defense System

An automated, AI-powered water gun turret that detects deer with computer vision and fires a water burst to protect tomato plants — no chemicals, no harm, fully autonomous.

## How It Works

1. A USB camera streams video continuously
2. YOLO-World (open-vocabulary object detection) identifies deer in the frame
3. Two servo motors aim a disassembled electric water gun at the target
4. A short water burst is triggered via a MOSFET/relay circuit
5. The system resets and keeps watching

Runs 24/7, fully local, no cloud required.

## Hardware

| Component | Details |
|---|---|
| Compute board | Orange Pi 5 (RK3588 NPU, 6 TOPS) |
| Camera | USB 1080p webcam (UVC-compatible) |
| Servos | 2× MG90S or MG996R (pan + tilt) |
| Servo driver | PCA9685 I²C PWM driver (optional) |
| Trigger | IRLZ44N MOSFET or 5V relay module |
| Water gun | Disassembled battery-powered toy water gun |
| OS | Armbian on Orange Pi 5 |

**Estimated cost**: $150–350 USD

## Repository Structure

```
deer-defense-project/
├── src/                  # Python source code
│   ├── main.py           # Entry point — detection + control loop
│   ├── detector.py       # YOLO-World inference wrapper
│   ├── servo_control.py  # Pan/tilt servo control
│   ├── trigger.py        # Water gun trigger (MOSFET/relay)
│   └── config.py         # Configuration (target class, thresholds, etc.)
├── docs/                 # Supporting documentation and diagrams
├── hardware/             # Wiring diagrams, BOM, mechanical notes
├── tests/                # Unit and integration tests
├── CLAUDE.md             # AI-assisted development guide
├── README.md
└── .gitignore
```

## Getting Started

### Prerequisites

```bash
sudo apt update && sudo apt install python3 python3-pip python3-venv git -y
```

### Install dependencies

```bash
python3 -m venv venv
source venv/bin/activate
pip install opencv-python numpy ultralytics
```

### Run (CPU/prototype mode)

```bash
python3 src/main.py
```

### Configuration

Edit `src/config.py` to set:
- `TARGET_CLASS` — text prompt for YOLO-World (default: `"deer"`)
- `CONFIDENCE_THRESHOLD` — detection confidence cutoff (default: `0.5`)
- `COOLDOWN_SECONDS` — delay between triggers (default: `3`)
- `BURST_DURATION` — water burst length in seconds (default: `0.5`)

## Development Phases

See [CLAUDE.md](CLAUDE.md) for the full 7-phase build plan, wiring details, and NPU acceleration guide.

## Contributing

Pull requests welcome. Open an issue first to discuss significant changes.

## License

MIT
