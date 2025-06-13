# collect_data.py
from pymongo import MongoClient
import gridfs
import numpy as np
import cv2
import re
from collections import defaultdict
import sys
import os
import pymongo
from PIL import Image  # Import the PIL library

# Add parent directory to Python path to find the module
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from death_calculation.tiefenberechnung_schleife import process_plant_data

def fetch_latest_data():
    """
    Fetches the latest image data and bounding box descriptions from MongoDB.
    """
    try:
        client = pymongo.MongoClient("mongodb://100.72.230.30:27017/")
        db = client["RoboGardener"]
        image_data = db["ImageData"]

        # Find the latest document
        latest_document = image_data.find_one(sort=[('_id', pymongo.DESCENDING)])

        if latest_document:
            left_img = latest_document["left_image"]
            right_img = latest_document["right_image"]
            bbox_text = latest_document["bounding_box_description"]
            return left_img, right_img, bbox_text
        else:
            print("No data found in MongoDB.")
            return None, None, None
    except pymongo.errors.ConnectionFailure as e:
        print(f"Could not connect to MongoDB: {e}")
        return None, None, None
    except Exception as e:
        print(f"An error occurred: {e}")
        return None, None, None

def fetch_latest_data_from_local(image_folder="calib_images"):
    """
    Fetches image data and bounding box descriptions from local files in the specified folder.
    This function is used as a fallback when MongoDB is not available.
    """
    try:
        # Get a list of image files in the folder
        image_files = [f for f in os.listdir(image_folder) if f.endswith((".jpg", ".jpeg", ".png")) and "left" in f]
        if not image_files:
            print(f"No left images found in {image_folder}")
            return None, None, None

        # Choose the first left image
        left_image_name = image_files[0]
        left_image_path = os.path.join(image_folder, left_image_name)
        right_image_name = left_image_name.replace("left", "right")
        right_image_path = os.path.join(image_folder, right_image_name)
        bbox_file_name = left_image_name.replace("left_plant", "bbox_plant").replace(".jpg", ".txt")
        bbox_file_path = os.path.join(image_folder, bbox_file_name)

        # Open the images using PIL
        try:
            left_img = Image.open(left_image_path)
            right_img = Image.open(right_image_path)

            # Convert images to bytes
            with open(left_image_path, "rb") as f:
                left_img_bytes = f.read()
            with open(right_image_path, "rb") as f:
                right_img_bytes = f.read()
        except FileNotFoundError:
            print(f"Image file not found: {left_image_path} or {right_image_path}")
            return None, None, None

        # Read the bounding box description from the file
        try:
            with open(bbox_file_path, "r") as f:
                bbox_text = f.read()
        except FileNotFoundError:
            print(f"Bounding box file not found: {bbox_file_path}")
            return None, None, None

        return left_img_bytes, right_img_bytes, bbox_text

    except Exception as e:
        print(f"An error occurred while reading local data: {e}")
        return None, None, None
