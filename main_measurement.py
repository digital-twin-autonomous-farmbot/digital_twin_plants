import os
from collect_data.collect_data import fetch_latest_data  # Import the local data function
from death_calculation.tiefenberechnung_schleife import process_plant_data
from plant_detection.request_plant_species import PlantIdentifier
from dotenv import load_dotenv
import yaml  # Import the YAML library

def main():
    print("Starting plant measurement process...")

    # Load environment variables
    dotenv_path = os.path.join(os.path.dirname(__file__), 'plant_detection', '.env')  # Construct the path to the .env file
    load_dotenv(dotenv_path)  # Load environment variables from the specified path
    api_key = os.getenv("API_KEY")
    if not api_key:
        raise RuntimeError("API_KEY not found in .env file.")

    # 1. Fetch latest image data from MongoDB
    print("\nFetching latest images...")
    left_img, right_img, bbox_text = fetch_latest_data()

    # 2. Calculate plant depth and height
    print("\nCalculating plant measurements...")
    results = process_plant_data(left_img, right_img, bbox_text)

    # 3. Identify plant species
    print("\nIdentifying plant species...")

    plant_id = PlantIdentifier(api_key)

    # Save the images to files (you might already have this in collect_data)
    left_image_path = "left_plant.jpg"
    right_image_path = "right_plant.jpg"
    with open(left_image_path, "wb") as f:
        f.write(left_img)
    with open(right_image_path, "wb") as f:
        f.write(right_img)

    # Identify one of the plants (e.g., the left one)
    identification_result = plant_id.identify_plant(left_image_path)
    formatted_result = plant_id.format_results(identification_result)

    print("\nPlant Identification Result:")
    print(formatted_result)

    # Extract plant type from formatted result (modify as needed based on format_results output)
    plant_type = formatted_result.split("Scientific Name: ")[1].split("\n")[0] if "Scientific Name: " in formatted_result else "Unknown"

    # Add plant type to results dictionary
    results["plant_type"] = plant_type

    # Save results to YAML file
    output_file = "plant_measurements.yaml"
    with open(output_file, "w") as yaml_file:
        yaml.dump(results, yaml_file, default_flow_style=False)  # Use default_flow_style=False for better readability

    print(f"\nResults saved to {output_file}")
    print("\nMeasurement process completed!")
    return results

if __name__ == "__main__":
    main()