import logging
from collect_data import fetch_latest_data

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def test_mongodb_connection():
    """Test if we can fetch data from MongoDB"""
    logger.info("Testing MongoDB fetch functionality...")
    
    left_img, right_img, bbox_text = fetch_latest_data()
    
    # Detailed component checking
    logger.info("\nChecking components:")
    logger.info(f"Left image present: {left_img is not None}")
    logger.info(f"Right image present: {right_img is not None}")
    logger.info(f"Bbox text present: {bbox_text is not None}")
    
    if all((left_img, right_img, bbox_text)):
        logger.info("\nData details:")
        logger.info(f"Left image size: {len(left_img)} bytes")
        logger.info(f"Right image size: {len(right_img)} bytes")
        logger.info(f"Bbox text length: {len(bbox_text)} chars")
        return True
    else:
        logger.error("\nFailed to fetch complete data set")
        logger.error("Some components are missing")
        return False

if __name__ == "__main__":
    test_mongodb_connection()