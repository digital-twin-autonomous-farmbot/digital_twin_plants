# Camera Calibration Module

This module contains the scripts and data necessary for calibrating a stereo camera system. Accurate camera calibration is crucial for accurate depth calculation.

## Contents

*   `stereo_calibration_opencv.py`: This script performs stereo camera calibration using OpenCV.
*   `stereo_calibration.yaml`: This YAML file stores the calibration parameters obtained from `stereo_calibration_opencv.py`. These parameters include camera matrices, distortion coefficients, rotation, and translation vectors.
*   `stereo_calibration_analysis.yaml`: This YAML file stores the Q matrix, which is derived from the calibration parameters and used for reprojecting the disparity map into a 3D point cloud.

## `stereo_calibration_opencv.py`

This script performs the following steps:

1.  **Detect Chessboard Corners:**
    *   Reads pairs of images (left and right) containing a chessboard pattern.
    *   Uses `cv2.findChessboardCorners` to detect the corners of the chessboard in each image. The chessboard size (number of inner corners) is defined by the `chessboard_size` variable.

2.  **Calibration:**
    *   Uses `cv2.calibrateCamera` to calibrate each camera individually. This function estimates the camera matrix (`mtx`) and distortion coefficients (`dist`) for each camera.
    *   Uses `cv2.stereoCalibrate` to perform stereo calibration. This function estimates the rotation (`R`) and translation (`T`) between the two cameras, as well as the essential matrix (`E`) and fundamental matrix (`F`).

3.  **Saving Calibration Data:**
    *   Saves all the calibration parameters (camera matrices, distortion coefficients, rotation, translation, essential matrix, and fundamental matrix) to a YAML file named `stereo_calibration.yaml` using `cv2.FileStorage`.

### Mathematical Background

The camera calibration process aims to estimate the intrinsic and extrinsic parameters of the camera system.

*   **Intrinsic Parameters:** These parameters describe the internal characteristics of the camera, such as the focal length, principal point, and distortion coefficients.
    *   **Camera Matrix (mtx):** A 3x3 matrix that maps 3D points in the camera coordinate system to 2D points in the image plane.
    *   **Distortion Coefficients (dist):** A vector that describes the lens distortion.

*   **Extrinsic Parameters:** These parameters describe the position and orientation of the camera in the world coordinate system.
    *   **Rotation (R):** A 3x3 rotation matrix that describes the orientation of the camera.
    *   **Translation (T):** A 3x1 translation vector that describes the position of the camera.

The calibration process involves solving a system of equations that relates the 3D coordinates of the chessboard corners to their 2D projections in the images. The OpenCV functions use the Zhang's algorithm to solve this system of equations.

### Usage

1.  **Capture Calibration Images:**
    *   Capture several pairs of images (left and right) of a chessboard pattern from different viewpoints.
    *   Ensure that the chessboard is clearly visible in all images.
    *   Place the images in the `calib_images` folder, named as `left_1.jpg`, `right_1.jpg`, etc.

2.  **Run the Calibration Script:**
    *   Execute `python stereo_calibration_opencv.py` to run the calibration script.
    *   The calibration parameters will be saved in `stereo_calibration.yaml`.

### Notes

*   Accurate camera calibration is crucial for accurate depth calculation.
*   The accuracy of the calibration depends on the quality of the calibration images and the number of images used.
*   The chessboard size should be chosen such that the chessboard covers a significant portion of the image.