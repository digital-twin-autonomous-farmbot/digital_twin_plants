# digital_twin_plants

This repository contains scripts and tools for the digital analysis and identification of plants, including calibration, plant species recognition, depth calculation, and result aggregation.

---

## Contents

- **calib_images/**  
  Folder for storing plant images to be processed.

- **plant_detection/**  
  Contains scripts for plant species identification using the Plant.id API.
  - `request_plant_species.py`: Handles API requests and result formatting.
  - `batch_identify_plants.py`: Automates batch processing of plant images and saves results.
  - `api_key.txt`: (Not included in repo) Place your Plant.id API key here.

- **results/**  
  Stores output files, such as identification results and depth calculation results.

- **death_calculation/**  
  Scripts for further analysis, such as sorting and statistical evaluation of results.

- **tiefenberechnung.py**  
  Script for calculating the depth (distance) of plants from stereo images. It typically takes a pair of left and right images, detects the plant in both, computes the disparity (pixel shift), and uses camera calibration parameters to estimate the real-world depth of the plant. The output is usually a depth value for a single plant or image pair.

- **tiefenberechnung_schleife.py**  
  Batch-processing script for depth calculation. It automates the process of running `tiefenberechnung.py` over multiple pairs of left/right plant images (e.g., `left_plant_1.jpg` and `right_plant_1.jpg`, etc.). For each pair, it calculates the depth and aggregates the results into a YAML or CSV file for further analysis. This script is useful for processing large datasets efficiently and consistently.

---

## Main Features

- **Calibration:**  
  Scripts for calibrating and preparing plant images for analysis.

- **Automated Plant Identification:**  
  Batch processing of plant images using the Plant.id API, with results saved for each image.

- **Depth Calculation:**  
  Calculation of plant distance from stereo images using computer vision techniques and camera calibration data.

- **Batch Depth Processing:**  
  Automated looping over multiple image pairs to calculate and store depth values for an entire dataset.

- **Result Aggregation and Analysis:**  
  Tools for grouping, sorting, and analyzing identification and depth calculation results.

---

## Usage

1. **API Key:**  
   - Obtain a Plant.id API key and save it in `plant_detection/api_key.txt`.
   - Add `api_key.txt` to your `.gitignore` to keep it private.

2. **Prepare Images:**  
   - Place your plant images in the `calib_images` folder, named as `left_plant_1.jpg`, `right_plant_1.jpg`, etc.

3. **Run Identification:**  
   - Execute `python plant_detection/batch_identify_plants.py` to process all images and save results in `results/all_plants_results.txt`.

4. **Run Depth Calculation:**  
   - For a single pair, use `tiefenberechnung.py` with the appropriate image paths and calibration data.
   - For batch processing, use `tiefenberechnung_schleife.py` to process all image pairs and aggregate the results.

5. **Analyze Results:**  
   - Use scripts in `death_calculation/` for further data analysis and visualization.

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
- Depth calculation scripts require proper camera calibration data for accurate results.

---

## License

This repository is for academic and research purposes. Please respect the terms of use for any third-party APIs or datasets.
