import cv2
import numpy as np
import yaml
import re
import glob
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

def extract_bbox_from_txt(bbox_text, label="potted plant"):
    """
    Extract bounding box coordinates from the bounding box description string.
    """
    for line in bbox_text.splitlines():  # Split the string into lines
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

def process_plant_data(left_img_bytes, right_img_bytes, bbox_text):
    """
    Processes the left and right image bytes and bounding box description to calculate plant depth and height.
    """
    # Kalibrierdaten aus YAML laden
    fs = cv2.FileStorage("../results/stereo_calibration.yaml", cv2.FILE_STORAGE_READ)
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
    Q = load_q_matrix("../results/stereo_calibration_analysis.yaml")

    # Decode image bytes
    imgL = cv2.imdecode(np.frombuffer(left_img_bytes, np.uint8), cv2.IMREAD_GRAYSCALE)
    imgR = cv2.imdecode(np.frombuffer(right_img_bytes, np.uint8), cv2.IMREAD_GRAYSCALE)

    # Check if the images were successfully decoded
    if imgL is None or imgR is None:
        print("Error decoding images. Check if the image data is valid.")
        return {}

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

    # Compute 3D points (depth)
    points_3D = compute_depth(disparity, Q)
    depth_map = points_3D[:, :, 2]

    # Bounding Box aus AI Detection laden und Debug-Ausgaben
    bbox = extract_bbox_from_txt(bbox_text)
    if bbox:
        x, y, w, h = bbox
        height, width = depth_map.shape

        ai_width = 2026
        ai_height = 1520

        scale_x = width / ai_width
        scale_y = height / ai_height

        x = int(x * scale_x)
        y = int(y * scale_y)
        w = int(w * scale_x)
        h = int(h * scale_y)

        bbox_corners = np.array([
            [x, y],
            [x + w, y],
            [x + w, y + h],
            [x, y + h]
        ], dtype=np.float32)

        bbox_disp = disparity[y:y+h, x:x+w]
        valid_disp = bbox_disp[np.isfinite(bbox_disp) & (bbox_disp > 0)]
        if valid_disp.size > 0:
            mean_disp = np.median(valid_disp)
        else:
            mean_disp = np.median(disparity[np.isfinite(disparity) & (disparity > 0)])

        pts_3d = []
        for cx, cy in bbox_corners:
            Z = focal_length * baseline / mean_disp
            X = (cx - mtx_l[0,2]) * Z / focal_length
            Y = (cy - mtx_l[1,2]) * Z / focal_length
            pts_3d.append([X, Y, Z])
        pts_3d = np.array(pts_3d, dtype=np.float32)

        pts_2d_left = bbox_corners.reshape(-1, 1, 2).astype(np.float32)
        pts_undist_left = cv2.undistortPoints(pts_2d_left, mtx_l, dist_l, P=mtx_l)
        pts_3d_right = (R @ pts_3d.T + T).T
        pts_2d_right, _ = cv2.projectPoints(pts_3d_right, np.zeros(3), np.zeros(3), mtx_r, dist_r)
        pts_2d_right = pts_2d_right.reshape(-1, 2)

        x_r, y_r, w_r, h_r = (
            int(np.min(pts_2d_right[:, 0])),
            int(np.min(pts_2d_right[:, 1])),
            int(np.max(pts_2d_right[:, 0]) - np.min(pts_2d_right[:, 0])),
            int(np.max(pts_2d_right[:, 1]) - np.min(pts_2d_right[:, 1]))
        )

        x = max(0, min(x, width-1))
        y = max(0, min(y, height-1))
        w = min(w, width - x)
        h = min(h, height - y)
        x_r = max(0, min(x_r, width-1))
        y_r = max(0, min(y_r, height-1))
        w_r = min(w_r, width - x_r)
        h_r = min(h_r, height - y_r)

        roi = depth_map[y:y+h, x:x+w]
        roi_valid = roi[np.isfinite(roi) & (roi > 0)]
        print(f"BBox links (skaliert): x={x}, y={y}, w={w}, h={h}")
        print(f"BBox rechts (projiziert): x={x_r}, y={y_r}, w={w_r}, h={h_r}")
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

    results = {
        'focal_length_px': float(focal_length),
        'baseline': float(baseline),
        'plant_height_cm': float(plant_height_cm),
        'top_depth_cm': float(top_depth),
        'bottom_depth_cm': float(bottom_depth),
        'mean_depth_cm': (float(top_depth) + float(bottom_depth)) / 2.0,
    }

    return results

if __name__ == "__main__":
    # This part is only for testing purposes and should not be part of the main script
    # Find all matching image pairs and bbox files
    left_images = sorted(glob.glob("../picture_taking_scripts/calib_images_ai/left_*.jpg"))
    right_images = sorted(glob.glob("../picture_taking_scripts/calib_images_ai/right_*.jpg"))
    bbox_files = sorted(glob.glob("../picture_taking_scripts/calib_images_ai/bbox_plant*.txt"))

    all_results = []

    for left_img, right_img, bbox_file in zip(left_images, right_images, bbox_files):
        print(f"\nProcessing: {os.path.basename(left_img)}, {os.path.basename(right_img)}, {os.path.basename(bbox_file)}")

        # Read image files as bytes
        with open(left_img, "rb") as f:
            left_img_bytes = f.read()
        with open(right_img, "rb") as f:
            right_img_bytes = f.read()

        # Read bounding box file
        with open(bbox_file, "r") as f:
            bbox_text = f.read()

        # Process the data
        results = process_plant_data(left_img_bytes, right_img_bytes, bbox_text)
        all_results.append(results)

    # Save results to YAML
    save_results_yaml("../results/tiefenberechnung_results.yaml", all_results)
