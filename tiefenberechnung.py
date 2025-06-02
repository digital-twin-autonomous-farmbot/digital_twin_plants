import cv2
import numpy as np
import yaml

def load_q_matrix(yaml_path):
    with open(yaml_path, "r") as f:
        calib = yaml.safe_load(f)
    Q = np.array(calib["Q"])
    return Q

def compute_depth(disparity, Q):
    # disparity: single-channel float32 image (output from stereo matcher)
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
valid_mask = np.isfinite(depth_map) & (depth_map > 0)

center_x = depth_map.shape[1] // 2
col = depth_map[:, center_x]
col_valid = col[np.isfinite(col) & (col > 0)]

if len(col_valid) > 60:
    top_depth = np.median(col_valid[10:30])
    bottom_depth = np.median(col_valid[-30:])
    plant_height_cm = abs(bottom_depth - top_depth)
else:
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
cv2.imshow("Tiefe", depth_vis)

cv2.waitKey(0)
cv2.destroyAllWindows()
