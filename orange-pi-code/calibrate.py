"""
calibrate.py — Fixed-camera calibration using AprilTags

Setup:
  1. Print several AprilTags (tag36h11 family) at 15cm width.
     Download from: https://github.com/AprilRobotics/apriltag-imgs
  2. Place tags around your garden at varied positions and distances.
     Put at least one tag at your maximum water range (~18 ft).
  3. Run:  python3 calibrate.py
  4. Use arrow keys to aim the turret at each highlighted tag,
     then press SPACE to record the point.
  5. After recording 6+ points, press C to compute and save calibration.

Controls:
  Arrow keys      — move turret (pan/tilt) by 1°
  Shift + arrows  — move turret by 5°
  SPACE           — record current tag + servo angles as a calibration point
  C               — compute homography and save calibration.json
  R               — reset / clear all recorded points
  Q               — quit without saving
"""

import json
import sys
import cv2
import numpy as np

import config
import servo_control

try:
    from pupil_apriltags import Detector
except ImportError:
    sys.exit("pupil-apriltags not installed. Run: pip install pupil-apriltags")

STEP_SMALL = 1.0    # degrees per arrow key press
STEP_LARGE = 5.0    # degrees per Shift+arrow key press

# Approximate deer height in pixels at MAX_WATER_RANGE_FT, derived from the
# furthest calibration tag using camera scale factor.
_scale_px_per_m = None   # pixels per metre at 1m distance (computed from tags)


def estimate_camera_scale(detector, frame, camera_matrix, dist_coeffs):
    """Detect tags and return the pixel-per-metre scale at 1m distance."""
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    tags = detector.detect(gray, estimate_tag_pose=True,
                           camera_params=_camera_params(camera_matrix),
                           tag_size=config.APRILTAG_SIZE_M)
    return tags


def _camera_params(camera_matrix):
    fx = camera_matrix[0, 0]
    fy = camera_matrix[1, 1]
    cx = camera_matrix[0, 2]
    cy = camera_matrix[1, 2]
    return (fx, fy, cx, cy)


def estimate_intrinsics():
    """Estimate camera intrinsics from frame size and a typical 70° horizontal FOV."""
    fx = config.FRAME_WIDTH / (2 * np.tan(np.radians(70 / 2)))
    fy = fx
    cx = config.FRAME_WIDTH / 2.0
    cy = config.FRAME_HEIGHT / 2.0
    K = np.array([[fx, 0, cx],
                  [0, fy, cy],
                  [0,  0,  1]], dtype=np.float64)
    return K


def draw_overlay(frame, tags, points, selected_tag_id):
    """Draw tag detections and recorded calibration points on the frame."""
    for tag in tags:
        corners = tag.corners.astype(int)
        cv2.polylines(frame, [corners], True, (0, 255, 0), 2)
        cx, cy = int(tag.center[0]), int(tag.center[1])
        cv2.circle(frame, (cx, cy), 6, (0, 255, 0), -1)

        dist_m = np.linalg.norm(tag.pose_t) if tag.pose_t is not None else 0
        dist_ft = dist_m * 3.28084
        label = f"ID:{tag.tag_id}  {dist_ft:.1f}ft"
        color = (0, 255, 255) if tag.tag_id == selected_tag_id else (0, 255, 0)
        cv2.putText(frame, label, (cx - 40, cy - 12),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.55, color, 2)

    for i, p in enumerate(points):
        cv2.circle(frame, (int(p["pixel"][0]), int(p["pixel"][1])), 8, (255, 100, 0), -1)
        cv2.putText(frame, f"#{i+1} {p['distance_ft']:.1f}ft",
                    (int(p["pixel"][0]) + 10, int(p["pixel"][1])),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.45, (255, 100, 0), 1)

    pan, tilt = servo_control.get_angles()
    hud = [
        f"Pan: {pan:.1f}  Tilt: {tilt:.1f}",
        f"Points recorded: {len(points)}  (need >= 6)",
        "ARROWS=aim  SPACE=record  C=calibrate  R=reset  Q=quit",
    ]
    for i, line in enumerate(hud):
        cv2.putText(frame, line, (12, 28 + i * 24),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 2)
    return frame


def compute_calibration(points):
    """Build homography from pixel coords → servo angles."""
    if len(points) < 4:
        print("Need at least 4 calibration points.")
        return None

    pixel_pts = np.array([[p["pixel"][0], p["pixel"][1]] for p in points],
                         dtype=np.float32)
    servo_pts = np.array([[p["pan"], p["tilt"]] for p in points],
                         dtype=np.float32)

    H, mask = cv2.findHomography(pixel_pts, servo_pts, cv2.RANSAC, 5.0)
    if H is None:
        print("Homography computation failed — check calibration points.")
        return None

    inliers = int(mask.sum())
    print(f"Homography computed — {inliers}/{len(points)} inlier points used.")
    return H


def compute_fire_zone(points):
    """Convex hull of calibration points within MAX_WATER_RANGE_FT."""
    in_range = [p for p in points if p["distance_ft"] <= config.MAX_WATER_RANGE_FT]
    if len(in_range) < 3:
        print(f"Warning: fewer than 3 in-range points for fire zone "
              f"(range = {config.MAX_WATER_RANGE_FT}ft). Using all points.")
        in_range = points

    pts = np.array([[p["pixel"][0], p["pixel"][1]] for p in in_range],
                   dtype=np.float32)
    hull = cv2.convexHull(pts)
    return hull.reshape(-1, 2).tolist()


def compute_min_bbox_height(points, camera_matrix):
    """Estimate minimum deer bounding box height at MAX_WATER_RANGE_FT."""
    max_range_m = config.MAX_WATER_RANGE_FT / 3.28084
    fy = camera_matrix[1, 1]
    # Angular height of a deer at max range; project to pixels using focal length
    min_height_px = int((config.DEER_HEIGHT_M / max_range_m) * fy)
    print(f"Min deer bbox height at {config.MAX_WATER_RANGE_FT}ft: {min_height_px}px")
    return min_height_px


def run():
    servo_control.init()
    cap = cv2.VideoCapture(config.CAMERA_INDEX)
    cap.set(cv2.CAP_PROP_FRAME_WIDTH, config.FRAME_WIDTH)
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, config.FRAME_HEIGHT)

    if not cap.isOpened():
        sys.exit("Could not open camera")

    K = estimate_intrinsics()
    at_detector = Detector(families=config.APRILTAG_FAMILY,
                           nthreads=2,
                           quad_decimate=2.0)

    points = []
    selected_tag_id = None

    print(__doc__)
    print(f"Max water range set to {config.MAX_WATER_RANGE_FT}ft (edit MAX_WATER_RANGE_FT in config.py to change).")

    while True:
        ret, frame = cap.read()
        if not ret:
            continue

        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        tags = at_detector.detect(gray, estimate_tag_pose=True,
                                  camera_params=_camera_params(K),
                                  tag_size=config.APRILTAG_SIZE_M)

        # Auto-select the closest tag to the frame center
        if tags:
            cx_frame, cy_frame = config.FRAME_WIDTH / 2, config.FRAME_HEIGHT / 2
            selected_tag_id = min(
                tags, key=lambda t: (t.center[0] - cx_frame)**2 + (t.center[1] - cy_frame)**2
            ).tag_id

        frame = draw_overlay(frame, tags, points, selected_tag_id)
        cv2.imshow("Calibrate — aim turret at each tag and press SPACE", frame)

        key = cv2.waitKey(30) & 0xFF
        pan, tilt = servo_control.get_angles()

        # Arrow key handling (with Shift for large steps)
        if key == 81 or key == ord('a'):    # Left arrow / a
            servo_control.move_to(pan - STEP_SMALL, tilt)
        elif key == 83 or key == ord('d'):  # Right arrow / d
            servo_control.move_to(pan + STEP_SMALL, tilt)
        elif key == 82 or key == ord('w'):  # Up arrow / w
            servo_control.move_to(pan, tilt - STEP_SMALL)
        elif key == 84 or key == ord('s'):  # Down arrow / s
            servo_control.move_to(pan, tilt + STEP_SMALL)
        elif key == ord('A'):               # Shift+left
            servo_control.move_to(pan - STEP_LARGE, tilt)
        elif key == ord('D'):               # Shift+right
            servo_control.move_to(pan + STEP_LARGE, tilt)
        elif key == ord('W'):               # Shift+up
            servo_control.move_to(pan, tilt - STEP_LARGE)
        elif key == ord('S'):               # Shift+down
            servo_control.move_to(pan, tilt + STEP_LARGE)

        elif key == ord(' '):
            # Record the selected tag at current servo angles
            selected = next((t for t in tags if t.tag_id == selected_tag_id), None)
            if selected is None:
                print("No tag selected — point the camera at an AprilTag first.")
            else:
                dist_m = float(np.linalg.norm(selected.pose_t))
                dist_ft = dist_m * 3.28084
                pan_now, tilt_now = servo_control.get_angles()
                pt = {
                    "tag_id": int(selected.tag_id),
                    "pixel": [float(selected.center[0]), float(selected.center[1])],
                    "pan": pan_now,
                    "tilt": tilt_now,
                    "distance_ft": round(dist_ft, 2),
                    "in_range": dist_ft <= config.MAX_WATER_RANGE_FT,
                }
                points.append(pt)
                print(f"Recorded point #{len(points)}: tag {pt['tag_id']} "
                      f"at ({pt['pixel'][0]:.0f}, {pt['pixel'][1]:.0f}) "
                      f"pan={pt['pan']:.1f}° tilt={pt['tilt']:.1f}° "
                      f"dist={pt['distance_ft']:.1f}ft "
                      f"{'IN RANGE' if pt['in_range'] else 'OUT OF RANGE'}")

        elif key == ord('c') or key == ord('C'):
            if len(points) < 6:
                print(f"Need at least 6 points — only have {len(points)}.")
                continue

            H = compute_calibration(points)
            if H is None:
                continue

            fire_zone = compute_fire_zone(points)
            min_bbox_h = compute_min_bbox_height(points, K)

            cal = {
                "homography": H.tolist(),
                "fire_zone_polygon": fire_zone,
                "min_deer_bbox_height": min_bbox_h,
                "max_range_ft": config.MAX_WATER_RANGE_FT,
                "points": points,
            }
            with open(config.CALIBRATION_FILE, "w") as f:
                json.dump(cal, f, indent=2)
            print(f"Calibration saved to {config.CALIBRATION_FILE}")
            break

        elif key == ord('r') or key == ord('R'):
            points.clear()
            print("Points cleared — start over.")

        elif key == ord('q') or key == ord('Q') or key == 27:
            print("Quit without saving.")
            break

    cap.release()
    cv2.destroyAllWindows()
    servo_control.deinit()


if __name__ == "__main__":
    run()
