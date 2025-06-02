import cv2
import numpy as np

# 🔧 Kalibrierdaten aus YAML laden
fs = cv2.FileStorage("stereo_calibration.yaml", cv2.FILE_STORAGE_READ)

mtx_l = fs.getNode("mtx_l").mat()
T = fs.getNode("T").mat()
fs.release()

# 📏 focal_length in Pixel (fx) und baseline in cm
focal_length = mtx_l[0, 0]
baseline = abs(T[0, 0])

print(f"f = {focal_length:.2f} px, B = {baseline:.2f} cm")

# 📂 Stereo-Bilder laden
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

# 🧮 Disparität berechnen
disparity = stereo.compute(imgL, imgR).astype(np.float32) / 16.0

# 📐 Tiefe berechnen
depth_map = np.zeros(disparity.shape, np.float32)
depth_map[disparity > 0] = (focal_length * baseline) / disparity[disparity > 0]

# 🌿 Pflanzenhöhe messen im Bildzentrum
center_x = depth_map.shape[1] // 2
col = depth_map[:, center_x]

top_depth = np.median(col[10:30][col[10:30] > 0])
bottom_depth = np.median(col[-30:][col[-30:] > 0])
plant_height_cm = abs(bottom_depth - top_depth)

print(f"📐 Geschätzte Pflanzenhöhe: {plant_height_cm:.2f} cm")

# 🖼️ Optionale Visualisierung
disp_vis = cv2.normalize(disparity, None, 0, 255, cv2.NORM_MINMAX)
cv2.imshow("Disparität", np.uint8(disp_vis))

depth_vis = cv2.normalize(depth_map, None, 0, 255, cv2.NORM_MINMAX)
cv2.imshow("Tiefe", np.uint8(depth_vis))

cv2.waitKey(0)
cv2.destroyAllWindows()
