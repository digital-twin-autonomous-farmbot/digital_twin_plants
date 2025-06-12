# collect_data.py
from pymongo import MongoClient
import gridfs
import numpy as np
import cv2
import re
from collections import defaultdict
import sys
import os

# Add parent directory to Python path to find the module
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from death_calculation.tiefenberechnung_schleife import process_plant_data

def fetch_latest_data(mongo_uri="mongodb://100.72.230.30:27017"):
    client = MongoClient(mongo_uri)
    db = client["plant_images"]
    fs = gridfs.GridFS(db)

    pattern = r'(left|right|bbox)_plant_(\d{8}_\d{6})\.(jpg|txt)'
    files_by_ts = defaultdict(dict)

    for f in fs.find():
        match = re.match(pattern, f.filename)
        if match:
            kind, ts, _ = match.groups()
            files_by_ts[ts][kind] = f.filename

    sorted_ts = sorted(ts for ts in files_by_ts if {'left', 'right', 'bbox'}.issubset(files_by_ts[ts]))
    latest_ts = sorted_ts[-1]
    latest_files = files_by_ts[latest_ts]

    def load_bytes(name):
        return fs.find_one({"filename": name}).read()

    left_img = cv2.imdecode(np.frombuffer(load_bytes(latest_files['left']), np.uint8), cv2.IMREAD_COLOR)
    right_img = cv2.imdecode(np.frombuffer(load_bytes(latest_files['right']), np.uint8), cv2.IMREAD_COLOR)
    
    # Check if bbox file exists
    if 'bbox' in latest_files:
        bbox_text = load_bytes(latest_files['bbox']).decode("utf-8")
    else:
        bbox_text = None  # Or some default value

    return left_img, right_img, bbox_text
