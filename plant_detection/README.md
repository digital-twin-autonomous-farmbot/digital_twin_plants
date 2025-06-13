# Plant Detection Module

This module contains the scripts for identifying plant species using the Plant.id API.

## Contents

*   `request_plant_species.py`: This script handles communication with the Plant.id API to identify plant species from images.

## `request_plant_species.py`

This script defines the `PlantIdentifier` class, which is responsible for:

1.  **Encoding the Image:**
    *   Takes an image path as input.
    *   Encodes the image as a base64 string for transmission to the Plant.id API.

2.  **Preparing the API Request:**
    *   Constructs a JSON payload containing the base64 encoded image and any specified modifiers or plant details.
    *   Sets the necessary headers, including the API key and content type.

3.  **Sending the API Request:**
    *   Sends a POST request to the Plant.id API endpoint with the JSON payload and headers.
    *   Handles potential network errors using `try...except` blocks.

4.  **Processing the API Response:**
    *   Parses the JSON response from the API.
    *   Handles potential JSON decoding errors.
    *   Returns the parsed JSON response.

5.  **Formatting the Results:**
    *   Provides a method to format the raw JSON response into a human-readable string.

### Usage

The `PlantIdentifier` class is used in the `main_measurement.py` script to identify the plant species in the left image.

1.  **Initialization:**
    *   The `PlantIdentifier` class is initialized with your Plant.id API key, which is loaded from a `.env` file.

2.  **Plant Identification:**
    *   The `identify_plant` method is called with the path to the left image.
    *   The `identify_plant` method encodes the image, sends it to the Plant.id API, and returns the API response.

3.  **Result Formatting:**
    *   The `format_results` method is called to format the API response into a human-readable string.

### Notes

*   The Plant.id API requires an API key. You can obtain an API key from the [Plant.id website](https://plant.id/).
*   The API key should be stored in a `.env` file in the `plant_detection` directory. This file is not included in the repository for security reasons. Add `.env` to your `.gitignore` file to prevent accidental commits of your API key.