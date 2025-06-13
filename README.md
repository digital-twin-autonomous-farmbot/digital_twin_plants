# digital_twin_plants

This repository contains scripts and tools for the digital analysis and identification of plants, including calibration, plant species recognition, depth calculation, result aggregation, and statistical analysis.

---

## Contents

- **calib_images/**  
  Folder for storing plant images to be processed. When MongoDB is unavailable, the `main_measurement.py` script will use images in this folder as a fallback. Images should be named following the convention `left_plant_1.jpg`, `right_plant_1.jpg`, and `bbox_plant_1.txt` for the corresponding bounding box file.

- **plant_detection/**  
  Contains scripts for plant species identification using the Plant.id API.
  - `request_plant_species.py`: Handles API requests and result formatting, optimized for single plant identification.
  - `batch_identify_plants.py`: (Deprecated) Originally for batch processing, but now single plant identification is integrated into the main pipeline.
  - `api_key.txt`: (Not included in repo) Place your Plant.id API key here.

- **results/**  
  Stores output files, such as identification results and depth calculation results.

- **death_calculation/**  
  Scripts for calculating plant depth and height from stereo images, and for analyzing the results.
  - `tiefenberechnung.py`: (Deprecated) Original script for depth calculation.
  - `tiefenberechnung_schleife.py`: Integrated into the main pipeline for depth calculation, taking image bytes and bounding box text as input.
  - `R_analysis/`: Contains R scripts for statistical analysis and visualization of the results, including correlation analysis of mean depth and height.

- **collect_data/**
  - `collect_data.py`: Fetches the latest image data and bounding box descriptions from MongoDB. Includes a fallback to local files in `calib_images` when MongoDB is unavailable.

- **main_measurement.py**  
  The main script that orchestrates the entire plant analysis pipeline.

- **calibration/**
  Contains scripts and data for camera calibration.
  - `stereo_calibration.py`: Script for performing stereo camera calibration.
  - `stereo_calibration.yaml`: YAML file containing the calibration parameters.
  - `stereo_calibration_analysis.yaml`: YAML file containing the Q matrix.

---

## Main Features

- **Data Acquisition:**  
  Fetches the latest plant images and bounding box data from MongoDB, with a fallback to local files.

- **Camera Calibration:**
  Scripts to calibrate stereo camera setup and generate necessary parameters for depth calculation.

- **Depth Calculation:**  
  Calculates plant depth and height from stereo images using computer vision techniques and camera calibration data.

- **Automated Plant Identification:**  
  Identifies plant species using the Plant.id API.

- **Result Aggregation:**  
  Combines depth measurements and plant identification results into a single YAML file.

- **Statistical Analysis:**
  R scripts for analyzing the correlation between mean depth and plant height.

---

## The Main Pipeline (main_measurement.py)

The `main_measurement.py` script implements the following pipeline:

1.  **Data Fetching:**  
    - Attempts to fetch the latest image data (left image, right image, bounding box description) from a MongoDB database using the `collect_data.py` script.
    - If MongoDB is unavailable, it falls back to reading the image data and bounding box description from local files in the `calib_images` folder.

2.  **Depth Calculation:**  
    - Calculates the plant depth and height using the `process_plant_data` function from `tiefenberechnung_schleife.py`. This function takes the left and right image data (as bytes) and the bounding box description as input.

3.  **Plant Identification:**  
    - Uses the Plant.id API (via `request_plant_species.py`) to identify the plant species in the left image.

4.  **Result Aggregation:**  
    - Combines the depth measurements (plant height, top depth, bottom depth, mean depth) and the plant identification result (plant type) into a single dictionary.

5.  **YAML Output:**  
    - Saves the combined results to a YAML file (`plant_measurements.yaml`) for further analysis.

---

## Usage

1. **API Key:**  
   - Obtain a Plant.id API key and save it in `plant_detection/.env` as `API_KEY=your_key`.
   - Ensure the `.env` file is in the `plant_detection` directory.
   - Add `.env` to your `.gitignore` to keep your API key private.

2. **Prepare Images (for local fallback):**  
   - Place your plant images in the `calib_images` folder, named as `left_plant_1.jpg`, `right_plant_1.jpg`, etc.
   - Create corresponding bounding box files named `bbox_plant_1.txt` in the same folder.

3.  **Camera Calibration:**
    - Run `stereo_calibration.py` to calibrate the stereo camera setup. Follow the instructions in the script to capture calibration images.
    - The calibration parameters will be saved in `stereo_calibration.yaml` and `stereo_calibration_analysis.yaml`.

4. **Run the Main Pipeline:**  
   - Execute `python main_measurement.py` to run the entire plant analysis pipeline. The results will be saved in `plant_measurements.yaml`.

5. **Analyze Results:**
   - Use the R scripts in `death_calculation/R_analysis/` to perform statistical analysis and visualize the results. The `analyze_correlation.R` script can be used to analyze the correlation between mean depth and plant height.

---

## Model Used

- **Plant.id API:**  
  Identification is performed using the Plant.id API, which leverages advanced machine learning models for plant species recognition.

- **Depth Calculation:**  
  Uses stereo vision algorithms and camera calibration parameters (e.g., focal length, baseline) to compute plant distances from image pairs.

---

## Notes

- The Plant.id API is a paid service; usage may be limited by your subscription.
- For more information on the Plant.id API, see the [official documentation](https://documenter.getpostman.com/view/24599534/2s93z5A4v2).
- Depth calculation scripts require proper camera calibration data (stored in `calibration/stereo_calibration.yaml` and `calibration/stereo_calibration_analysis.yaml`) for accurate results.
- The `main_measurement.py` script assumes that the MongoDB server is running and accessible. If MongoDB is unavailable, it will automatically fall back to using local files.

---

## License

This repository is for academic and research purposes. Please respect the terms of use for any third-party APIs or datasets.
