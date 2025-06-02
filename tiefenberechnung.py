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

# 🔧 StereoSGBM verwenden (besser als StereoBM!)
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

# Example: get Z (depth) values
depth_map = points_3D[:, :, 2]
print("Depth map shape:", depth_map.shape)
print("Sample depth values:", depth_map[240, 320])

# Pflanzenhöhe messen im Bildzentrum
center_x = depth_map.shape[1] // 2
col = depth_map[:, center_x]

top_depth = np.median(col[10:30][col[10:30] > 0])
bottom_depth = np.median(col[-30:][col[-30:] > 0])
plant_height_cm = abs(bottom_depth - top_depth)

print(f"📐 Geschätzte Pflanzenhöhe: {plant_height_cm:.2f} cm")

# Optionale Visualisierung
disp_vis = cv2.normalize(disparity, None, 0, 255, cv2.NORM_MINMAX)
cv2.imshow("Disparität", np.uint8(disp_vis))

depth_vis = cv2.normalize(depth_map, None, 0, 255, cv2.NORM_MINMAX)
cv2.imshow("Tiefe", np.uint8(depth_vis))

cv2.waitKey(0)
cv2.destroyAllWindows()
