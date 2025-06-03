import requests
import base64
import json
from pathlib import Path

class PlantIdentifier:
    def __init__(self, api_key):
        """
        Initialize the Plant Identifier with your API key
        
        Args:
            api_key (str): Your Plant.id API key
        """
        self.api_key = api_key
        self.base_url = "https://api.plant.id/v2/identify"  # <-- FIXED ENDPOINT
        
    def encode_image(self, image_path):
        """
        Encode image to base64 string
        
        Args:
            image_path (str): Path to the image file
            
        Returns:
            str: Base64 encoded image string
        """
        try:
            with open(image_path, "rb") as image_file:
                encoded_string = base64.b64encode(image_file.read()).decode('utf-8')
                return encoded_string
        except FileNotFoundError:
            raise FileNotFoundError(f"Image file not found: {image_path}")
        except Exception as e:
            raise Exception(f"Error encoding image: {str(e)}")
    
    def identify_plant(self, image_path, modifiers=None, plant_details=None):
        """
        Identify a plant from an image

        Args:
            image_path (str): Path to the plant image
            modifiers (list): Deprecated, not used in API v3
            plant_details (list): Optional details like ["common_names", "url", "description"]

        Returns:
            dict: API response with plant identification results
        """
        # Default plant details
        if plant_details is None:
            plant_details = ["common_names", "url", "description", "taxonomy", "rank"]

        # Encode the image
        try:
            base64_image = self.encode_image(image_path)
            print(f"✓ Image encoded successfully. Size: {len(base64_image)} characters")
        except Exception as e:
            return {"error": str(e)}

        # Prepare the request payload (no modifiers, use similar_images top-level)
        payload = {
            "images": [base64_image],
            "plant_details": plant_details,
            "similar_images": True
        }

        # Prepare headers
        headers = {
            "Api-Key": self.api_key,
            "Content-Type": "application/json"
        }

        print(f"✓ API Key length: {len(self.api_key)} characters")
        print(f"✓ Request URL: {self.base_url}")
        print(f"✓ similar_images: True")
        print(f"✓ Plant details: {plant_details}")

        try:
            # Make the API request
            print("Sending request to API...")
            response = requests.post(self.base_url, json=payload, headers=headers)

            print(f"Response status code: {response.status_code}")
            print(f"Response headers: {dict(response.headers)}")

            if response.status_code != 200:
                print(f"Response content: {response.text}")

            response.raise_for_status()

            return response.json()

        except requests.exceptions.RequestException as e:
            return {"error": f"API request failed: {str(e)}"}
        except json.JSONDecodeError:
            return {"error": "Failed to parse API response"}
    
    def format_results(self, api_response):
        """
        Format the API response into readable plant information
        
        Args:
            api_response (dict): Raw API response
            
        Returns:
            str: Formatted plant identification results
        """
        if "error" in api_response:
            return f"Error: {api_response['error']}"
        
        if not api_response.get("suggestions"):
            return "No plant identification found."
        
        results = []
        results.append("🌱 PLANT IDENTIFICATION RESULTS 🌱\n")
        results.append("=" * 50)
        
        for i, suggestion in enumerate(api_response["suggestions"][:3], 1):  # Top 3 results
            probability = suggestion.get("probability", 0) * 100
            plant_name = suggestion.get("plant_name", "Unknown")
            
            results.append(f"\n#{i} Match ({probability:.1f}% confidence):")
            results.append(f"   Scientific Name: {plant_name}")
            
            # Common names
            if "plant_details" in suggestion and "common_names" in suggestion["plant_details"]:
                common_names = suggestion["plant_details"]["common_names"]
                if common_names:
                    results.append(f"   Common Names: {', '.join(common_names[:3])}")
            
            # Taxonomy
            if "plant_details" in suggestion and "taxonomy" in suggestion["plant_details"]:
                taxonomy = suggestion["plant_details"]["taxonomy"]
                if taxonomy.get("family"):
                    results.append(f"   Family: {taxonomy['family']}")
                if taxonomy.get("genus"):
                    results.append(f"   Genus: {taxonomy['genus']}")
            
            # Description
            if "plant_details" in suggestion and "description" in suggestion["plant_details"]:
                description = suggestion["plant_details"]["description"]
                if description and "value" in description:
                    desc_text = description["value"][:200] + "..." if len(description["value"]) > 200 else description["value"]
                    results.append(f"   Description: {desc_text}")
        
        return "\n".join(results)


def main():
    """
    Main function - replace with your actual API key and image path
    """
    # Replace with your actual API key
    API_KEY = "UF39VaQdDki3Kc7C0y9lPEO9G8oEn7okQyF36rs7J00sVxpHVE"
    
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


