# Camera Calibration Guide

This guide walks through calibrating the fixed camera so the turret servo system accurately aims at targets detected in the camera frame, and so the water gun only fires when a deer is within effective range (~18 ft).

---

## Why Calibration Is Needed

The camera is mounted in a fixed position separate from the turret. When the camera sees a deer at pixel (px, py), the turret must aim at a slightly different angle to compensate for the physical offset between the camera lens and the turret pivot. This offset causes parallax error — larger at short distances, smaller at long distances.

Calibration maps camera pixel coordinates directly to servo angles using a set of real-world reference points, eliminating this error automatically.

Calibration also defines two range-limiting safeguards:
- **Fire zone polygon** — the region of the camera frame that corresponds to within water gun range (~18 ft). Deer outside this area are not fired at.
- **Minimum bounding box height** — if the deer appears too small in the frame it is too far away for the water to reach. The trigger is skipped.

---

## What You Need

### AprilTags
AprilTags are printed square markers that the camera detects with sub-pixel accuracy and can estimate the distance to.

See the full printing and preparation instructions: [AprilTag Printing Guide](apriltag-printing-guide.md)

**Quick summary:** Print tags `00000`–`00009` from the `tag36h11` family at exactly **15 cm wide** on plain white paper (laser printer preferred). Mount on rigid boards attached to garden stakes.

### Placement
- Place tags at **varied positions and distances** across the garden area you want to protect
- Cover the full angular range the turret will need to sweep (left, right, near, far)
- Place **at least 2 tags at or near your maximum water range** (~18 ft from the turret)
- Place **at least 2 tags at close range** (~6–10 ft) for near-field accuracy
- Aim for **6–9 tags total** visible in the camera frame simultaneously if possible; you can also move tags and record additional points in multiple passes

```
Example layout (top-down view):

        Camera (fixed)
             |
    [Tag 5]  |  [Tag 6]     <-- ~6 ft
   [Tag 3]   |   [Tag 4]    <-- ~12 ft
  [Tag 1]    |    [Tag 2]   <-- ~18 ft (max water range)
             |
          [Turret]
        (pan/tilt mount)
```

---

## Running the Calibration Script

```bash
cd deer-defense-project
source venv/bin/activate
python3 orange-pi-code/calibrate.py
```

A live camera window will open showing the detected AprilTags highlighted in green with their ID and estimated distance.

### Controls

| Key | Action |
|---|---|
| ← → ↑ ↓ arrow keys | Move turret 1° at a time |
| Shift + arrow keys | Move turret 5° at a time |
| `SPACE` | Record current tag + servo angles as a calibration point |
| `C` | Compute homography and save `calibration.json` |
| `R` | Clear all recorded points and start over |
| `Q` / `Esc` | Quit without saving |

### Step-by-Step Procedure

1. Run the script — the camera feed opens and tags are highlighted automatically
2. The tag closest to the center of the frame is auto-selected (yellow label)
3. Use arrow keys to aim the turret at that tag until the water gun points directly at it
4. Press **Space** — the script records the pixel location, servo angles, and distance
5. Repeat for each tag around the garden (move the turret to each one in turn)
6. Aim to record **at least 6 points** — more points = more accurate calibration
7. Once you have enough points, press **C** to compute and save

### What Gets Saved — `calibration.json`

```json
{
  "homography": [[...3x3 matrix...]],
  "fire_zone_polygon": [[px, py], [px, py], ...],
  "min_deer_bbox_height": 191,
  "max_range_ft": 18.0,
  "points": [ ... raw calibration data ... ]
}
```

- **homography** — the 3×3 transform matrix used by `servo_control.py` to convert pixel coordinates to servo angles
- **fire_zone_polygon** — convex hull of all in-range calibration points; used by `trigger.py` to block firing outside the protected area
- **min_deer_bbox_height** — minimum bounding box pixel height for a deer to be considered within water gun range; computed from focal length and `DEER_HEIGHT_M` in `config.py`

---

## Verifying Calibration

After saving, test accuracy before deploying:

```bash
python3 orange-pi-code/calibrate.py
```

Re-run the script (which loads the saved calibration automatically on next run of `main.py`) and observe whether the turret tracks to each tag accurately. If a tag is detected and you manually compare where the turret is pointing, error should be under 2–3° at typical garden distances.

---

## Re-Calibration

Re-calibrate whenever:
- The camera is moved or its angle changes
- The turret mount is repositioned
- You change `MAX_WATER_RANGE_FT` in `config.py`
- You extend coverage to a different part of the garden

Simply re-run `calibrate.py` and overwrite `calibration.json`.

---

## Troubleshooting

| Problem | Likely cause | Fix |
|---|---|---|
| No tags detected | Poor lighting, tag too small, or blurry print | Improve lighting; reprint tags larger |
| Distance reads incorrectly | `APRILTAG_SIZE_M` in config doesn't match printed size | Measure printed tag and update config |
| Homography fails | Too few points or collinear points | Add more points spread across the frame |
| Turret overshoots tags | Smoothing too low | Increase `SMOOTHING` in `servo_control.py` |
| Fire zone too small | Range tags placed too close | Move range-limit tags to ~18 ft and recalibrate |
