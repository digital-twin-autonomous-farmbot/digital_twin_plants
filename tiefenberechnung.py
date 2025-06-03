import cv2
import numpy as np
import yaml
import re

def load_q_matrix(yaml_path):
    with open(yaml_path, "r") as f:
        calib = yaml.safe_load(f)
    Q = np.array(calib["Q"])
    return Q

def compute_depth(disparity, Q):
    points_3D = cv2.reprojectImageTo3D(disparity, Q)
    return points_3D

def save_results_yaml(filename, focal_length, baseline, plant_height_cm, top_depth, bottom_depth):
    data = {
        'focal_length_px': float(focal_length),
        'baseline': float(baseline),
        'plant_height_cm': float(plant_height_cm),
        'top_depth_cm': float(top_depth),
        'bottom_depth_cm': float(bottom_depth)
    }
    with open(filename, "w") as f:
        yaml.dump(data, f)

def extract_bbox_from_txt(txt_path):
    with open(txt_path, "r") as f:
        for line in f:
            match = re.search(r'@ (\d+),(\d+) (\d+)x(\d+)', line)
            if match:
                x = int(match.group(1))
                y = int(match.group(2))
                w = int(match.group(3))
                h = int(match.group(4))
                return x, y, w, h
    return None

# Kalibrierdaten aus YAML laden
fs = cv2.FileStorage("stereo_calibration.yaml", cv2.FILE_STORAGE_READ)
mtx_l = fs.getNode("mtx_l").mat()
T = fs.getNode("T").mat()
fs.release()

# focal_length in Pixel (fx) und baseline in cm
focal_length = mtx_l[0, 0]
baseline = abs(T[0, 0])

print(f"f = {focal_length:.2f} px, B = {baseline:.2f} cm")

# Stereo-Bilder laden
imgL = cv2.imread("calib_images/left_plant01.jpg", cv2.IMREAD_GRAYSCALE)
imgR = cv2.imread("calib_images/right_plant01.jpg", cv2.IMREAD_GRAYSCALE)

# StereoSGBM verwenden
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

# Disparität berechnen
disparity = stereo.compute(imgL, imgR).astype(np.float32) / 16.0

# Load Q matrix
Q = load_q_matrix("stereo_calibration_analysis.yaml")

# Compute 3D points (depth)
points_3D = compute_depth(disparity, Q)

# Z (depth) values extrahieren und ungültige Werte maskieren
depth_map = points_3D[:, :, 2]

# Bounding Box aus AI Detection laden und Debug-Ausgaben
bbox = extract_bbox_from_txt("calib_images/bbox_plant01.txt")
if bbox:
    x, y, w, h = bbox
    height, width = depth_map.shape

    # --- Bounding Box von AI-Detektionsbild auf aktuelle Bildgröße skalieren ---
    # Werte ggf. anpassen, falls dein AI-Detektionsbild andere Maße hat!
    ai_width = 2026
    ai_height = 1520

    scale_x = width / ai_width
    scale_y = height / ai_height

    x = int(x * scale_x)
    y = int(y * scale_y)
    w = int(w * scale_x)
    h = int(h * scale_y)

    # Bounding Box auf Bildgrenzen beschränke
    # nicht skalieren sondern beschneiden(crop)
    x = max(0, min(x, width-1))
    y = max(0, min(y, height-1))
    w = min(w, width - x)
    h = min(h, height - y)
    # --- Ende Skalierung ---

    roi = depth_map[y:y+h, x:x+w]
    roi_valid = roi[np.isfinite(roi) & (roi > 0)]
    print(f"BBox (skaliert): x={x}, y={y}, w={w}, h={h}")
    print(f"Bildgröße: {depth_map.shape}")
    print(f"ROI shape: {roi.shape}, gültige Werte: {roi_valid.size}")
    if roi_valid.size > 60:
        top_band = roi[0:10, :][np.isfinite(roi[0:10, :]) & (roi[0:10, :] > 0)]
        bottom_band = roi[-10:, :][np.isfinite(roi[-10:, :]) & (roi[-10:, :] > 0)]
        print(f"Top-Band gültige Werte: {top_band.size}, Bottom-Band gültige Werte: {bottom_band.size}")
        top_depth = np.median(top_band) if top_band.size > 0 else float('nan')
        bottom_depth = np.median(bottom_band) if bottom_band.size > 0 else float('nan')
        plant_height_cm = abs(bottom_depth - top_depth)
    else:
        print("Zu wenig gültige Werte im ROI!")
        top_depth = bottom_depth = plant_height_cm = float('nan')
else:
    print("No bounding box found!")
    top_depth = bottom_depth = plant_height_cm = float('nan')

print(f"Geschätzte Pflanzenhöhe: {plant_height_cm:.2f} cm")

# Ergebnisse als YAML speichern
save_results_yaml(
    "tiefenberechnung_results.yaml",
    focal_length,
    baseline,
    plant_height_cm,
    top_depth,
    bottom_depth
)

# Optionale Visualisierung
disp_vis = cv2.normalize(disparity, None, 0, 255, cv2.NORM_MINMAX)
cv2.imshow("Disparität", np.uint8(disp_vis))

# Nur gültige Tiefenwerte für die Visualisierung verwenden
depth_vis = np.zeros_like(depth_map, dtype=np.uint8)
valid = np.isfinite(depth_map) & (depth_map > 0)
if np.any(valid):
    minv = np.percentile(depth_map[valid], 2)
    maxv = np.percentile(depth_map[valid], 98)
    normed = np.clip((depth_map - minv) / (maxv - minv) * 255, 0, 255)
    depth_vis[valid] = normed[valid].astype(np.uint8)
    # Draw bounding box for visualization
    if bbox:
        cv2.rectangle(depth_vis, (x, y), (x+w, y+h), 255, 2)
cv2.imshow("Tiefe", depth_vis)

cv2.waitKey(0)
cv2.destroyAllWindows()
