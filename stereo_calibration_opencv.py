import numpy as np
import cv2
import glob

# Schachbrettgröße (Anzahl innerer Ecken)
chessboard_size = (9, 6)
square_size = 1.0  # Kann 1.0 sein, wenn wir nur relativ messen

# Objektpunkte (3D)
objp = np.zeros((np.prod(chessboard_size), 3), np.float32)
objp[:, :2] = np.indices(chessboard_size).T.reshape(-1, 2)
objp *= square_size

objpoints = []  # 3D Punkte
imgpoints_left = []
imgpoints_right = []

images_left = sorted(glob.glob("calib_images/left_*.jpg"))
images_right = sorted(glob.glob("calib_images/right_*.jpg"))

for left_img_path, right_img_path in zip(images_left, images_right):
    img_left = cv2.imread(left_img_path)
    img_right = cv2.imread(right_img_path)
    gray_left = cv2.cvtColor(img_left, cv2.COLOR_BGR2GRAY)
    gray_right = cv2.cvtColor(img_right, cv2.COLOR_BGR2GRAY)

    ret_left, corners_left = cv2.findChessboardCorners(gray_left, chessboard_size)
    ret_right, corners_right = cv2.findChessboardCorners(gray_right, chessboard_size)

    if ret_left and ret_right:
        objpoints.append(objp)
        imgpoints_left.append(corners_left)
        imgpoints_right.append(corners_right)

print(f"Anzahl gültiger Bildpaare: {len(objpoints)}")

# Einzel-Kalibrierung
ret_l, mtx_l, dist_l, _, _ = cv2.calibrateCamera(objpoints, imgpoints_left, gray_left.shape[::-1], None, None)
ret_r, mtx_r, dist_r, _, _ = cv2.calibrateCamera(objpoints, imgpoints_right, gray_right.shape[::-1], None, None)

# Stereo-Kalibrierung
flags = 0
criteria = (cv2.TERM_CRITERIA_EPS + cv2.TERM_CRITERIA_MAX_ITER, 30, 1e-6)
ret, _, _, _, _, R, T, E, F = cv2.stereoCalibrate(
    objpoints, imgpoints_left, imgpoints_right,
    mtx_l, dist_l, mtx_r, dist_r,
    gray_left.shape[::-1], criteria=criteria, flags=flags
)

# Speichere alle Kalibrierdaten in YAML
fs = cv2.FileStorage("stereo_calibration.yaml", cv2.FILE_STORAGE_WRITE)

fs.write("mtx_l", mtx_l)
fs.write("dist_l", dist_l)
fs.write("mtx_r", mtx_r)
fs.write("dist_r", dist_r)
fs.write("R", R)
fs.write("T", T)
fs.write("E", E)
fs.write("F", F)

fs.release()
print("✅ Kalibrierdaten gespeichert in stereo_calibration.yaml")
