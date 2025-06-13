# Depth Calculation Module

This module contains the scripts and functions necessary for calculating the depth and height of plants from stereo image pairs. The core script is `tiefenberechnung_schleife.py`, which implements the depth calculation pipeline.

## `tiefenberechnung_schleife.py`

This script performs the following steps:

1.  **Loading Calibration Data:**
    *   Loads the stereo camera calibration parameters from `results/stereo_calibration.yaml`. This file contains the intrinsic parameters of the left and right cameras (camera matrix `mtx_l`, `mtx_r` and distortion coefficients `dist_l`, `dist_r`), as well as the rotation `R` and translation `T` between the two cameras.
    *   Loads the Q matrix from `results/stereo_calibration_analysis.yaml`. The Q matrix is used to reproject the disparity map into a 3D point cloud.

2.  **Image Loading and Preprocessing:**
    *   Takes the left and right image data as byte strings.
    *   Decodes the image bytes into grayscale images using `cv2.imdecode`.

3.  **Stereo Matching:**
    *   Uses the StereoSGBM algorithm (`cv2.StereoSGBM_create`) to compute the disparity map between the left and right images. The StereoSGBM algorithm is a semi-global block matching algorithm that estimates the disparity by finding the best match for each pixel in the left image in the right image.
    *   The parameters of the StereoSGBM algorithm are tuned to optimize the disparity map quality.

4.  **Depth Map Calculation:**
    *   Reprojects the disparity map into a 3D point cloud using the Q matrix (`cv2.reprojectImageTo3D`). The Q matrix transforms the (x, y, disparity) values into (X, Y, Z) 3D coordinates.
    *   Extracts the depth map (Z-coordinate) from the 3D point cloud.

5.  **Bounding Box Processing:**
    *   Extracts the bounding box coordinates from the bounding box description string. The bounding box is assumed to be in the format produced by an object detection algorithm.
    *   Scales the bounding box coordinates to match the size of the depth map.

6.  **Plant Height Estimation:**
    *   Extracts the region of interest (ROI) from the depth map based on the bounding box coordinates.
    *   Calculates the top and bottom depth values by taking the median depth value in the top and bottom bands of the ROI.
    *   Estimates the plant height as the absolute difference between the bottom and top depth values.

7.  **Result Aggregation:**
    *   Stores the calculated depth values (top depth, bottom depth, plant height) along with the calibration parameters (focal length, baseline) in a dictionary.

### Mathematical Background

The depth calculation relies on the principles of stereo vision. The key equations are:

*   **Disparity:** The disparity (d) is the difference in pixel coordinates between the corresponding points in the left and right images.

*   **Depth (Z):** The depth (Z) of a point is inversely proportional to the disparity:

    ```
    Z = (focal_length * baseline) / disparity
    ```

    where:
    *   `focal_length` is the focal length of the camera.
    *   `baseline` is the distance between the two cameras.

*   **3D Coordinates (X, Y, Z):** The 3D coordinates of a point can be calculated from the disparity and the camera parameters using the Q matrix. The Q matrix is a 4x4 matrix that is derived from the camera intrinsic and extrinsic parameters. The `cv2.reprojectImageTo3D` function performs this transformation.

### Dependencies

*   `cv2` (OpenCV): For image processing and stereo matching.
*   `numpy`: For numerical calculations.
*   `yaml`: For loading calibration data.

### Usage

This script is integrated into the main pipeline (`main_measurement.py`) and is not intended to be run directly. The `main_measurement.py` script passes the image data and bounding box description to the `process_plant_data` function in this script.

### Notes

*   Accurate camera calibration is crucial for accurate depth calculation.
*   The performance of the stereo matching algorithm depends on the quality of the images and the tuning of the algorithm parameters.
*   The accuracy of the plant height estimation depends on the accuracy of the bounding box and the quality of the depth map.