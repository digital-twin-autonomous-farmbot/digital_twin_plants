# collect_data.py
import os
import sys
import logging
from pymongo import MongoClient
from gridfs import GridFS
from datetime import datetime
from dotenv import load_dotenv

# Add parent directory to Python path to find the module
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from death_calculation.tiefenberechnung_schleife import process_plant_data

# Load environment variables from .env file
load_dotenv()

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def connect_to_mongodb():
    """Establish a connection to the MongoDB database."""
    try:
        client = MongoClient(os.getenv("MONGODB_URI"))
        logger.info("Connected to MongoDB")
        return client
    except Exception as e:
        logger.error(f"Error connecting to MongoDB: {str(e)}")
        return None

def fetch_latest_data():
    """Fetches the latest image data and bounding box descriptions from MongoDB using GridFS."""
    client = connect_to_mongodb()
    if not client:
        logger.error("MongoDB connection failed")
        return None, None, None
        
    try:
        db = client.plant_images
        fs = GridFS(db)

        # Find latest files with detailed error checking
        latest_left = fs.find_one({"filename": {"$regex": "^left_plant_.*\.jpg$"}}, sort=[("uploadDate", -1)])
        if not latest_left:
            logger.error("Left image not found in GridFS")
            return None, None, None

        latest_right = fs.find_one({"filename": {"$regex": "^right_plant_.*\.jpg$"}}, sort=[("uploadDate", -1)])
        if not latest_right:
            logger.error("Right image not found in GridFS")
            return None, None, None

        latest_bbox = fs.find_one({"filename": {"$regex": "^bbox_plant_.*\.txt$"}}, sort=[("uploadDate", -1)])
        if not latest_bbox:
            logger.error("Bbox file not found in GridFS")
            return None, None, None

        logger.info(f"Found files:")
        logger.info(f"Left image: {latest_left.filename}")
        logger.info(f"Right image: {latest_right.filename}")
        logger.info(f"Bbox file: {latest_bbox.filename}")

        try:
            left_data = latest_left.read()
            right_data = latest_right.read()
            bbox_data = latest_bbox.read().decode('utf-8')
            
            logger.info(f"Successfully read - Left: {len(left_data)} bytes, "
                       f"Right: {len(right_data)} bytes, "
                       f"Bbox: {len(bbox_data)} chars")
                       
            return left_data, right_data, bbox_data
            
        except Exception as e:
            logger.error(f"Error reading file data: {str(e)}")
            return None, None, None

    except Exception as e:
        logger.error(f"Error accessing MongoDB: {str(e)}")
        return None, None, None
    finally:
        client.close()

def store_plant_data(left_image_data, right_image_data, bbox_text):
    """Store plant data in MongoDB using GridFS with timestamped filenames"""
    client = connect_to_mongodb()
    if not client:
        return False
        
    try:
        db = client.plant_images
        fs = GridFS(db)
        
        # Generate timestamp for filenames
        timestamp = datetime.now().strftime("%Y.%m.%d_%H:%M:%S")
        
        # Store images in GridFS with timestamped filenames
        left_id = fs.put(
            left_image_data, 
            filename=f'left_plant_{timestamp}.jpg'
        )
        right_id = fs.put(
            right_image_data, 
            filename=f'right_plant_{timestamp}.jpg'
        )
        bbox_id = fs.put(
            bbox_text.encode('utf-8'), 
            filename=f'bbox_plant_{timestamp}.txt'
        )
        
        logger.info(f"Stored files with timestamp {timestamp}")
        logger.info(f"Left image ID: {left_id}")
        logger.info(f"Right image ID: {right_id}")
        logger.info(f"Bbox file ID: {bbox_id}")
        
        return True
        
    except Exception as e:
        logger.error(f"Error storing data: {str(e)}")
        return False
    finally:
        client.close()
