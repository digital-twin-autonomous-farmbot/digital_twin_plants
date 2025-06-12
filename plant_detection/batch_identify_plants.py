import os
from .request_plant_species import PlantIdentifier  # Added dot for relative import
from pymongo import MongoClient
import gridfs
import numpy as np
import cv2
import re
from collections import defaultdict

def load_api_key(api_key_file="api_key.txt"):
    try:
        with open(api_key_file, "r", encoding="utf-8") as f:
            return f.read().strip()
    except FileNotFoundError:
        raise RuntimeError(f"API key file '{api_key_file}' not found. Please create it and add your API key.")

def fetch_latest_images(mongo_uri="mongodb://100.72.230.30:27017"):
    client = MongoClient(mongo_uri)
    db = client["plant_images"]
    fs = gridfs.GridFS(db)

    pattern = r'(left|right)_plant_(\d{8}_\d{6})\.jpg'
    files_by_ts = defaultdict(dict)

    for f in fs.find():
        match = re.match(pattern, f.filename)
        if match:
            kind, ts = match.groups()
            files_by_ts[ts][kind] = f

    sorted_ts = sorted(ts for ts in files_by_ts if {'left', 'right'}.issubset(files_by_ts[ts]))
    latest_ts = sorted_ts[-1]
    latest_files = files_by_ts[latest_ts]

    return latest_files['left'], latest_files['right']

def identify_plant_from_mongo(api_key, result_file):
    plant_id = PlantIdentifier(api_key)
    left_file, right_file = fetch_latest_images()

    with open(result_file, "w", encoding="utf-8") as out:
        for side, image_file in [("left", left_file), ("right", right_file)]:
            image_data = image_file.read()
            # Convert GridFS file to temporary file for Plant.id API
            temp_path = f"temp_{side}.jpg"
            with open(temp_path, "wb") as temp_file:
                temp_file.write(image_data)

            out.write(f"\n=== Results for {image_file.filename} ===\n")
            print(f"Processing {image_file.filename} ...")
            result = plant_id.identify_plant(temp_path)
            formatted_result = plant_id.format_results(result)
            out.write(formatted_result)
            out.write("\n" + "="*60 + "\n")
            print(f"Results for {image_file.filename} appended to {result_file}")

            # Clean up temporary file
            os.remove(temp_path)

if __name__ == "__main__":
    # Set your API key and result file path
    API_KEY = load_api_key("api_key.txt")
    RESULT_FILE = os.path.join("results", "latest_plant_results.txt")

    os.makedirs("results", exist_ok=True)
    identify_plant_from_mongo(API_KEY, RESULT_FILE)