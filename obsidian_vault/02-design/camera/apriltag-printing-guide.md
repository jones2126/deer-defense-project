# AprilTag Printing Guide

AprilTags are black-and-white square markers that the calibration script detects with high accuracy and uses to estimate distance. Print quality directly affects how reliably the camera detects them — a blurry or incorrectly sized tag will cause calibration errors.

---

## Which Tags to Print

Use the **tag36h11** family — the default in `config.py` and the most widely supported family in robotics.

**Download individual tag images here:**
https://github.com/AprilRobotics/apriltag-imgs/tree/master/tag36h11

Each file is named `tag36_11_XXXXX.png` where `XXXXX` is the tag ID (00000, 00001, 00002, etc.).

**Print tags with these IDs:** `00000` through `00009` (10 tags) — enough for a full calibration with spares.

---

## Print Size

The script uses **15 cm (5.9 inches)** as the expected tag width (`APRILTAG_SIZE_M = 0.15` in `config.py`). This is used to calculate distance — if the printed size does not match this value, distance estimates will be wrong.

> If you print at a different size, update `APRILTAG_SIZE_M` in `config.py` to match **before** running `calibrate.py`.

**Recommended print sizes:**

| Distance from camera | Recommended tag size | `APRILTAG_SIZE_M` value |
|---|---|---|
| Up to 15 ft | 10 cm (4 in) | 0.10 |
| Up to 25 ft | 15 cm (6 in) | 0.15 ← default |
| Up to 35 ft | 20 cm (8 in) | 0.20 |

For this project (max range ~18 ft) the default 15 cm is appropriate.

---

## How to Print

### Option A — Print directly from the browser (simplest)

1. Open the tag image on GitHub (e.g. `tag36_11_00000.png`)
2. Right-click → **Save image as** — save to your computer
3. Open in any image viewer or Word/Google Docs
4. Set the image size to exactly **15 cm × 15 cm** (or 5.9" × 5.9")
5. Print at 100% scale — do **not** use "fit to page"

### Option B — Print multiple tags per page (more efficient)

1. Download all 10 tag `.png` files
2. Open a document (Word, Google Docs, LibreOffice)
3. Insert each image and set each to exactly **15 cm × 15 cm**
4. Leave at least **2 cm of white border** around each tag — the white border is part of the tag and required for detection
5. Print at 100% — verify no scaling is applied in the print dialog

### Printer Settings

| Setting | Value |
|---|---|
| Paper | Plain white, 80gsm or heavier |
| Color | Black & white (grayscale) |
| Quality | High / Best |
| Scale | 100% — never "fit to page" or "shrink to fit" |
| Paper size | Letter (US) or A4 |

> **Laser printer preferred** — inkjet can bleed ink into fine details, reducing detection reliability especially at distance. If you only have inkjet, use the highest DPI setting available.

---

## Verify Before Using

After printing, measure the outer black border of the tag with a ruler.

- It should be **exactly 15 cm** (or whatever size you chose)
- If it is off by more than 3 mm, reprint and check your print dialog for scaling

Also check visually:
- The black squares should have sharp, clean edges — no blurring or ink spread
- The white areas inside the tag should be bright white, not gray
- The white border around the outside should be at least 1–2 cm wide

---

## Mounting for Outdoor Use

The tags need to survive outdoor conditions during calibration (wind, moisture, sunlight).

**Simple method:**
1. Print on plain paper
2. Glue or tape to a piece of **rigid foam board or cardboard** (available at dollar stores)
3. Laminate if possible — even a self-adhesive laminating sheet helps against morning dew
4. Attach to a garden stake, bamboo pole, or tent peg with tape or cable ties

**Positioning tips:**
- Face the tags toward the camera — they must be roughly perpendicular to the camera's line of sight for accurate pose estimation
- Avoid placing tags in deep shadow or in direct bright sun that causes glare
- Keep tags at least 30 cm above the ground so grass doesn't obscure the bottom edge

---

## Quick Reference

| Item | Value |
|---|---|
| Tag family | tag36h11 |
| Tag IDs to print | 00000 – 00009 |
| Print size | 15 cm × 15 cm |
| White border | ≥ 1 cm on all sides |
| `APRILTAG_SIZE_M` in config | 0.15 |
| Download URL | https://github.com/AprilRobotics/apriltag-imgs/tree/master/tag36h11 |

See [Calibration Guide](calibration-guide.md) for placement and the calibration procedure.
