# Picture Taking Scripts

This folder contains scripts for capturing stereo images of plants using two Raspberry Pi cameras.

## take_picture_and_upload.py

This script automates the process of capturing stereo images and performing object detection. It:

1. **Captures Stereo Images**
   - Takes synchronized pictures from two cameras (left: camera 0, right: camera 1)
   - Uses `libcamera-jpeg` with resolution 640x480
   - Images are named using timestamps (e.g., `left_plant_20230815_123456.jpg`)

2. **Performs Object Detection**
   - Uses `rpicam-hello` with MobileNet SSD model
   - Runs on the right camera image
   - Generates bounding box data for detected objects
   - Prints detection results in real-time to the terminal
   - Saves detection data to a text file in the format:
     ```
     timestamp_detection.txt
     ```
   - Uses subprocess to capture both stdout and stderr:
     ```python
     result = subprocess.run(
         command,
         stdout=subprocess.PIPE,
         stderr=subprocess.STDOUT,  # Capture both stdout and stderr
         text=True  # Output will be a string, not bytes
     )
     ```

3. **Handles Data Storage**
   - Uploads images to a remote server (endpoint: `http://100.72.230.30:6000/upload`)
   - Stores data in MongoDB with:
     - Timestamp
     - Left image
     - Right image
     - Bounding box detection data

### Usage

```bash
python take_picture_and_upload.py
```

### Requirements

- Raspberry Pi with two cameras configured
- MongoDB server running on localhost:27017
- `libcamera-jpeg` and `rpicam-hello` installed
- Python packages: `requests`, `pymongo`

### Configuration

The script uses these default settings:
- Image resolution: 640x480
- MongoDB URI: `mongodb://localhost:27017/`
- Database name: `plant_images`
- Collection name: `images`
- Image API endpoint: