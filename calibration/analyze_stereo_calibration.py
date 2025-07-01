import cv2
import numpy as np
import yaml
import glob

def load_stereo_calibration(yaml_path):
    fs = cv2.FileStorage(yaml_path, cv2.FILE_STORAGE_READ)
    mtx_l = fs.getNode("mtx_l").mat()
    dist_l = fs.getNode("dist_l").mat()
    mtx_r = fs.getNode("mtx_r").mat()
    dist_r = fs.getNode("dist_r").mat()
    R = fs.getNode("R").mat()
    T = fs.getNode("T").mat()
    fs.release()
    return mtx_l, dist_l, mtx_r, dist_r, R, T

def compute_rectification(mtx_l, dist_l, mtx_r, dist_r, R, T, image_size):
    R1, R2, P1, P2, Q, _, _ = cv2.stereoRectify(
        mtx_l, dist_l, mtx_r, dist_r, image_size, R, T, flags=cv2.CALIB_ZERO_DISPARITY, alpha=0
    )
    return R1, R2, P1, P2, Q

def save_results_yaml(filename, mtx_l, mtx_r, T, Q):
    data = {
        'mtx_l': mtx_l.tolist(),
        'mtx_r': mtx_r.tolist(),
        'T': T.tolist(),
        'Q': Q.tolist()
    }
    with open(filename, "w") as f:
        yaml.dump(data, f)

def main():
    yaml_path = "../results/stereo_calibration.yaml"

    # Automatische Bildgrößenerkennung
    img_path = sorted(glob.glob("../picture_taking_scripts/calib_images/left_*.jpg"))[0]
    img = cv2.imread(img_path)
    image_size = (img.shape[1], img.shape[0])

    mtx_l, dist_l, mtx_r, dist_r, R, T = load_stereo_calibration(yaml_path)
    print("Left Camera Matrix:\n", mtx_l)
    print("Right Camera Matrix:\n", mtx_r)
    print("Translation Vector:\n", T)

    R1, R2, P1, P2, Q = compute_rectification(mtx_l, dist_l, mtx_r, dist_r, R, T, image_size)
    print("Disparity-to-Depth Mapping Matrix (Q):\n", Q)

    # Save results to YAML file
    save_results_yaml("../results/stereo_calibration_analysis.yaml", mtx_l, mtx_r, T, Q)

if __name__ == "__main__":
    main()
