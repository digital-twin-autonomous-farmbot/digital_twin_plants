import os
from request_plant_species import PlantIdentifier

def load_api_key(api_key_file="api_key.txt"):
    try:
        with open(api_key_file, "r", encoding="utf-8") as f:
            return f.read().strip()
    except FileNotFoundError:
        raise RuntimeError(f"API key file '{api_key_file}' not found. Please create it and add your API key.")

def batch_identify_plants(api_key, image_folder, result_file, indices):
    plant_id = PlantIdentifier(api_key)
    with open(result_file, "w", encoding="utf-8") as out:
        for i in indices:
            for side in ["left", "right"]:
                image_name = f"{side}_plant{i}.jpg"
                image_path = os.path.join(image_folder, image_name)
                out.write(f"\n=== Results for {image_name} ===\n")
                print(f"Processing {image_path} ...")
                result = plant_id.identify_plant(image_path)
                formatted_result = plant_id.format_results(result)
                out.write(formatted_result)
                out.write("\n" + "="*60 + "\n")
                print(f"Results for {image_name} appended to {result_file}")

if __name__ == "__main__":
    # Set your API key and folders here
    API_KEY = load_api_key("api_key.txt")
    IMAGE_FOLDER = "calib_images"
    RESULT_FILE = os.path.join("results", "all_plants_results.txt")
    INDICES = range(1, 16)  # Change as needed

    os.makedirs("results", exist_ok=True)
    batch_identify_plants(API_KEY, IMAGE_FOLDER, RESULT_FILE, INDICES)