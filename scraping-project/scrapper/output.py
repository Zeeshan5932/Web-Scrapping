import json
import os

# Function to extract only the 'full_text_of_notice' from the JSON data
def extract_notice_text(json_file, output_file):
    try:
        # Open the existing JSON file with the correct encoding
        with open(json_file, 'r', encoding='utf-8', errors='ignore') as f:  # Added encoding and error handling
            data = json.load(f)

        # Extract only the full_text_of_notice for each notice entry
        extracted_notices = {}
        for key, value in data.items():
            # Check if the value is a dictionary
            if isinstance(value, list) and value:  # Skipping empty lists
                extracted_notices[key] = [entry.get("full_text_of_notice") for entry in value if entry.get("full_text_of_notice") != "Not Available"]
            else:
                print(f"⚠️ Skipping key '{key}' because it does not map to a dict or it is empty.")
                
        # Save the extracted data into a new JSON file
        with open(output_file, 'w', encoding='utf-8') as out_f:
            json.dump(extracted_notices, out_f, indent=4, ensure_ascii=False)

        print(f"Extraction successful! Data saved to {output_file}")
    
    except Exception as e:
        print(f"An error occurred: {e}")

# Example usage
json_file = r"F:\eFaida\scraping-project\data\public_notices.json"  # Replace with the correct path
output_file = "extracted_notices.json"  # This will store the extracted data

# Run the extraction
extract_notice_text(json_file, output_file)
