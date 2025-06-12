import requests
import json
import base64

class PlantIdentifier:
    def __init__(self, api_key):
        """
        Initialize the Plant Identifier with your API key
        
        Args:
            api_key (str): Your Plant.id API key
        """
        self.api_key = api_key
        self.api_endpoint = "https://api.plant.id/v2/identify"

    def identify_plant(self, image_path):
        """
        Identify a plant from an image

        Args:
            image_path (str): Path to the plant image

        Returns:
            dict: API response with plant identification results
        """
        with open(image_path, "rb") as file:
            image_data = file.read()

        base64_image = base64.b64encode(image_data).decode("utf-8")
        
        payload = {
            "api_key": self.api_key,
            "images": [base64_image],
            "modifiers": ["crops_fast", "similar_images"],
            "plant_language": "en",
            "plant_details": ["common_names", "url", "wiki_description"]
        }

        try:
            response = requests.post(self.api_endpoint, json=payload)
            response.raise_for_status()  # Raise HTTPError for bad responses (4xx or 5xx)
            return response.json()
        except requests.exceptions.RequestException as e:
            print(f"API request failed: {e}")
            return {"error": str(e)}
        except json.JSONDecodeError as e:
            print(f"JSON decoding failed: {e}, Response text: {response.text}")
            return {"error": "Failed to decode JSON response"}

    def format_results(self, result):
        """
        Format the API response into readable plant information
        
        Args:
            result (dict): Raw API response
            
        Returns:
            str: Formatted plant identification results
        """
        output = []
        if "suggestions" in result:
            for suggestion in result["suggestions"][:3]:  # Top 3 suggestions
                confidence = suggestion.get("probability", 0) * 100
                plant_name = suggestion.get("plant_name", "Unknown")
                common_names = suggestion.get("plant_details", {}).get("common_names", [])
                
                output.append(f"Plant Name: {plant_name}")
                output.append(f"Confidence: {confidence:.1f}%")
                if common_names:
                    output.append(f"Common Names: {', '.join(common_names[:3])}")
                output.append("-" * 40)
                
        return "\n".join(output)


def main():
    """
    Main function - replace with your actual API key and image path
    """
    # Replace with your actual API key
    API_KEY = "api_key.txt"  # Path to your API key file
    
    # Replace with path to your plant image
    image_path = "calib_images/left_plant15.jpg"
    
    # Initialize the plant identifier
    plant_id = PlantIdentifier(API_KEY)
    
    print("Identifying plant...")
    print("This may take a few seconds...\n")
    
    # Identify the plant
    result = plant_id.identify_plant(image_path)
    
    # Format and display results
    formatted_result = plant_id.format_results(result)
    print(formatted_result)


if __name__ == "__main__":
    main()


