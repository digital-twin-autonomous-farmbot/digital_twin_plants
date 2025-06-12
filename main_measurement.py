import os
from collect_data.collect_data import fetch_latest_data
from plant_detection.batch_identify_plants import identify_plant_from_mongo
from death_calculation.tiefenberechnung_schleife import process_plant_data

def main():
    print("Starting plant measurement process...")

    # 1. Fetch latest image data from MongoDB
    print("\nFetching latest images...")
    left_img, right_img, bbox_text = fetch_latest_data()

    # 2. Calculate plant depth and height
    print("\nCalculating plant measurements...")
    results = process_plant_data(left_img, right_img, bbox_text)

    # 3. Identify plant species
    print("\nIdentifying plant species...")
    script_dir = os.path.dirname(os.path.abspath(__file__))
    api_key_path = os.path.join(script_dir, "plant_detection", "api_key.txt")
    result_file = os.path.join(script_dir, "results", "latest_plant_results.txt")
    
    # Create results directory if it doesn't exist
    os.makedirs(os.path.join(script_dir, "results"), exist_ok=True)
    
    identify_plant_from_mongo(api_key_path, result_file)

    print("\nMeasurement process completed!")
    return results

if __name__ == "__main__":
    main()