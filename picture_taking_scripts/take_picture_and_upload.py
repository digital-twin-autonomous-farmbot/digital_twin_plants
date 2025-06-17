import subprocess
import requests
import datetime
from pymongo import MongoClient
import logging

# Configure logging
logging.basicConfig(level=logging.DEBUG)
logging.getLogger('pymongo').setLevel(logging.DEBUG)

# Configuration
IMAGE_API_ENDPOINT = "http://100.72.230.30:6000/upload"  # Change to match your image_api IP
IMG_WIDTH = 640
IMG_HEIGHT = 480

# MongoDB configuration
MONGO_URI = "mongodb://localhost:27017/"
DB_NAME = "plant_images"
COLLECTION_NAME = "images"

# Initialize MongoDB client
client = MongoClient(MONGO_URI)
db = client[DB_NAME]
collection = db[COLLECTION_NAME]

def capture_image(camera_id: int, filename: str) -> bytes:
    """Capture image from camera and return it as bytes"""
    result = subprocess.run(
        [
            "libcamera-jpeg",
            f"--camera", str(camera_id),
            "--width", str(IMG_WIDTH),
            "--height", str(IMG_HEIGHT),
            "-o", "-"  # Output to stdout
        ],
        capture_output=True,
        check=True
    )
    return result.stdout

def run_bounding_box(camera_id: int) -> str:
    """Run rpicam-hello with AI model and return bounding box output as string"""
    result = subprocess.run(
        [
            "rpicam-hello",
            "--camera", str(camera_id),
            "--timeout", "1s",
            "--post-process-file", "/usr/share/rpi-camera-assets/imx500_mobilenet_ssd.json",
            "--width", str(IMG_WIDTH),
            "--height", str(IMG_HEIGHT),
            "--output", "/dev/null",
            "--verbose"
        ],
        capture_output=True,
        text=True,
        check=True
    )
    return result.stdout

def upload_file(data: bytes, filename: str, content_type: str = "application/octet-stream"):
    """Send the data to the image API via HTTP POST"""
    response = requests.post(
        IMAGE_API_ENDPOINT,
        files={"file": (filename, data, content_type)}
    )
    if response.ok:
        print(f"Uploaded {filename}: {response.text}")
    else:
        print(f"Upload failed for {filename}: {response.status_code} {response.text}")

def main():
    timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")

    # Capture images
    left_image = capture_image(0, f"left_plant_{timestamp}.jpg")
    right_image = capture_image(1, f"right_plant_{timestamp}.jpg")

    # Run bounding box AI
    bbox_text = run_bounding_box(1)

    # Add this debug code where you read the bbox file
    content = bbox_text
    print("File content before upload:", content)
    print("File size:", len(content), "bytes")

    # Upload all files
    upload_file(left_image, f"left_plant_{timestamp}.jpg", "image/jpeg")
    upload_file(right_image, f"right_plant_{timestamp}.jpg", "image/jpeg")
    upload_file(bbox_text.encode("utf-8"), f"bbox_plant_{timestamp}.txt", "text/plain")

    # MongoDB document
    document = {
        "timestamp": timestamp,
        "left_image": f"left_plant_{timestamp}.jpg",
        "right_image": f"right_plant_{timestamp}.jpg",
        "bbox_data": content
    }

    # Before inserting into MongoDB
    print("Document to be inserted:", document)
    # Check if bbox content is present in the document
    if "bbox_content" in document:
        print("bbox content length:", len(document["bbox_content"]))

    # Add logging for the MongoDB operation
    result = collection.insert_one(document)
    print("MongoDB insert result:", result.inserted_id)
    print("Inserted document:", collection.find_one({"_id": result.inserted_id}))

if __name__ == "__main__":
    main()
