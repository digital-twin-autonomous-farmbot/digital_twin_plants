import cv2
import numpy as np
import yaml
import re
import os

def load_q_matrix(yaml_path):
    with open(yaml_path, "r") as f:
        calib = yaml.safe_load(f)
    Q = np.array(calib["Q"])
    return Q

def compute_depth(disparity, Q):
    points_3D = cv2.reprojectImageTo3D(disparity, Q)
    return points_3D

def save_results_yaml(filename, results):
    with open(filename, "w") as f:
        yaml.dump(results, f)

def extract_bbox_from_txt(txt_path, label="potted plant"):
    with open(txt_path, "r") as f:
        for line in f:
            match = re.search(r'\[\d+\] : ([\w\s]+)\[\d+\].*@ (\d+),(\d+) (\d+)x(\d+)', line)
            if match:
                obj_label = match.group(1).strip()
                if obj_label == label:
                    x = int(match.group(2))
                    y = int(match.group(3))
                    w = int(match.group(4))
                    h = int(match.group(5))
                    return x, y, w, h
    return None

# Kalibrierdaten aus YAML laden
fs = cv2.FileStorage("results/stereo_calibration.yaml", cv2.FILE_STORAGE_READ)
mtx_l = fs.getNode("mtx_l").mat()
mtx_r = fs.getNode("mtx_r").mat()
dist_l = fs.getNode("dist_l").mat()
dist_r = fs.getNode("dist_r").mat()
R = fs.getNode("R").mat()
T = fs.getNode("T").mat()
fs.release()

# focal_length in Pixel (fx) und baseline in cm
focal_length = mtx_l[0, 0]
baseline = abs(T[0, 0]) / 10.0

print(f"f = {focal_length:.2f} px, B = {baseline:.2f} cm")

# Load Q matrix
Q = load_q_matrix("results/stereo_calibration_analysis.yaml")

results = []

def process_plant_data(left_image, right_image, bbox_data):
    """Process a stereo image pair and return depth calculations"""
    # Convert images to grayscale if they're not already
    if isinstance(left_image, str):
        imgL = cv2.imread(left_image, cv2.IMREAD_GRAYSCALE)
        imgR = cv2.imread(right_image, cv2.IMREAD_GRAYSCALE)
    elif len(left_image.shape) == 3:
        imgL = cv2.cvtColor(left_image, cv2.COLOR_BGR2GRAY)
        imgR = cv2.cvtColor(right_image, cv2.COLOR_BGR2GRAY)
    else:
        imgL = left_image
        imgR = right_image

    # Create stereo matcher
    stereo = cv2.StereoSGBM_create(
        minDisparity=0,
        numDisparities=64,
        blockSize=5,
        P1=8 * 3 * 5 ** 2,
        P2=32 * 3 * 5 ** 2,
        disp12MaxDiff=1,
        uniquenessRatio=10,
        speckleWindowSize=100,
        speckleRange=32
    )

    # Calculate disparity and depth
    disparity = stereo.compute(imgL, imgR).astype(np.float32) / 16.0
    points_3D = compute_depth(disparity, Q)
    depth_map = points_3D[:, :, 2]

    # Process bounding box if provided
    if bbox_data:
        bbox = extract_bbox_from_txt(bbox_data)
        if bbox is None:
            top_depth = bottom_depth = plant_height_cm = float('nan')
        else:
            x, y, w, h = bbox
            height, width = depth_map.shape

            # Scale bounding box if needed
            ai_width = 2026
            ai_height = 1520
            scale_x = width / ai_width
            scale_y = height / ai_height

            x = int(x * scale_x)
            y = int(y * scale_y)
            w = int(w * scale_x)
            h = int(h * scale_y)

            roi = depth_map[y:y+h, x:x+w]
            roi_valid = roi[np.isfinite(roi) & (roi > 0)]

            if roi_valid.size > 60:
                top_band = roi[0:10, :][np.isfinite(roi[0:10, :]) & (roi[0:10, :] > 0)]
                bottom_band = roi[-10:, :][np.isfinite(roi[-10:, :]) & (roi[-10:, :] > 0)]
                
                top_depth = np.median(top_band) if top_band.size > 0 else float('nan')
                bottom_depth = np.median(bottom_band) if bottom_band.size > 0 else float('nan')
                plant_height_cm = abs(bottom_depth - top_depth)
            else:
                top_depth = bottom_depth = plant_height_cm = float('nan')
    else:
        top_depth = bottom_depth = plant_height_cm = float('nan')

    return {
        'plant_height_cm': float(plant_height_cm),
        'top_depth_cm': float(top_depth),
        'bottom_depth_cm': float(bottom_depth),
        'mean_depth': (float(top_depth) + float(bottom_depth)) / 2.0,
        'focal_length_px': float(focal_length),
        'baseline': float(baseline)
    }

# Ergebnisse als YAML speichern
with open("results/tiefenberechnung_results.yaml", "w") as f:
    yaml.safe_dump(results, f)

# --- Optionale Visualisierung (GUI) ---
# To activate, uncomment the following block:
"""
disp_vis = cv2.normalize(disparity, None, 0, 255, cv2.NORM_MINMAX)
cv2.imshow("Disparität", np.uint8(disp_vis))

depth_vis = np.zeros_like(depth_map, dtype=np.uint8)
valid = np.isfinite(depth_map) & (depth_map > 0)
if np.any(valid):
    minv = np.percentile(depth_map[valid], 2)
    maxv = np.percentile(depth_map[valid], 98)
    normed = np.clip((depth_map - minv) / (maxv - minv) * 255, 0, 255)
    depth_vis[valid] = normed[valid].astype(np.uint8)
    if bbox:
        cv2.rectangle(depth_vis, (x, y), (x+w, y+h), 255, 2)
        cv2.rectangle(depth_vis, (x_r, y_r), (x_r+w_r, y_r+h_r), 128, 2)
cv2.imshow("Tiefe", depth_vis)

cv2.waitKey(0)
cv2.destroyAllWindows()
"""