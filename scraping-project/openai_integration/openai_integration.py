# import openai
# import json
# from dotenv import load_dotenv
# import os

# # Load environment variables from .env file
# load_dotenv()

# # Set the OpenAI API key from the .env file
# openai.api_key = os.getenv('OPENAI_API_KEY')

# def extract_data_from_notice(notice_text):
#     prompt = f"""
# You are a data extraction assistant. Extract the following fields from the provided legal/business notice.

# Return the result **strictly** as a valid JSON object with these exact keys:
# - notice_date
# - publication_name
# - location_name
# - street_address
# - city
# - state
# - zip_code
# - auction_site_used
# - count_of_tenants
# - all_tenants
# - full_notice_text

# Format:
# {{
#   "notice_date": "",
#   "publication_name": "",
#   "location_name": "",
#   "street_address": "",
#   "city": "",
#   "state": "",
#   "zip_code": "",
#   "auction_site_used": "",
#   "count_of_tenants": 0,
#   "all_tenants": [],
#   "full_notice_text": ""
# }}

# Ensure double quotes only and valid JSON output.

# Notice:
# \"\"\"{notice_text}\"\"\"
# """

#     try:
#         response = openai.ChatCompletion.create(
#             model="gpt-3.5-turbo",
#             messages=[{"role": "user", "content": prompt}],
#             temperature=0  # helps reduce variability
#         )

#         result = response['choices'][0]['message']['content']

#         extracted_data = json.loads(result)

#         # Optional: add the full notice text if missing
#         if "full_notice_text" not in extracted_data:
#             extracted_data["full_notice_text"] = notice_text.strip()

#         return extracted_data

#     except json.JSONDecodeError:
#         print(f"[ERROR] Failed to parse OpenAI response as JSON:\n{result}")
#         return None

#     except Exception as e:
#         print(f"[EXCEPTION] {str(e)}")
#         return None

#================================== code 2 ===================================

# import openai
# import json
# from dotenv import load_dotenv
# import os

# # Load environment variables from .env file
# load_dotenv()

# # Set the OpenAI API key from the .env file
# openai.api_key = os.getenv('OPENAI_API_KEY')

# def extract_data_from_notice(notice_text):
#     prompt = f"""
# You are a data extraction assistant. Extract the following fields from the provided legal/business notice.

# Return the result **strictly** as a valid JSON object with these exact keys:
# - notice_date
# - publication_name
# - location_name
# - street_address
# - city
# - state
# - zip_code
# - auction_site_used
# - count_of_tenants
# - all_tenants
# - full_notice_text

# Format:
# {{
#   "notice_date": "",
#   "publication_name": "",
#   "location_name": "",
#   "street_address": "",
#   "city": "",
#   "state": "",
#   "zip_code": "",
#   "auction_site_used": "",
#   "count_of_tenants": 0,
#   "all_tenants": [],
#   "full_notice_text": ""
# }}

# Ensure double quotes only and valid JSON output.

# Notice:
# \"\"\"{notice_text}\"\"\"
# """

#     try:
#         response = openai.ChatCompletion.create(
#             model="gpt-4o-mini",
#             messages=[{"role": "user", "content": prompt}],
#             temperature=0  # helps reduce variability
#         )

#         result = response['choices'][0]['message']['content']

#         extracted_data = json.loads(result)

#         # Optional: add the full notice text if missing
#         if "full_notice_text" not in extracted_data:
#             extracted_data["full_notice_text"] = notice_text.strip()

#         return extracted_data

#     except json.JSONDecodeError:
#         print(f"[ERROR] Failed to parse OpenAI response as JSON:\n{result}")
#         return None

#     except Exception as e:
#         print(f"[EXCEPTION] {str(e)}")
#         return None
# # ============   extra =============
# # def extract_notices_from_panels(notice_panels):
# #     all_notices = {}

# #     # Loop through the panels and process each one
# #     for index, panel in enumerate(notice_panels):
# #         notice_id = f"notice-{index + 1}"  # Create unique key like "notice-1", "notice-2", etc.
        
# #         # Extract full notice text
# #         full_text = panel.get("full_notice_text", "").strip()
        
# #         # Extract data from the notice using the extraction function
# #         extracted_data = extract_data_from_notice(full_text)
        
# #         if extracted_data:
# #             # Add the extracted data to the all_notices dictionary with the unique key
# #             all_notices[notice_id] = extracted_data
    
# #     # Save the all_notices dictionary to JSON
# #     with open("F:\eFaida\scraping-project\data\final.json", "w", encoding="utf-8") as f:
# #         json.dump(all_notices, f, indent=2, ensure_ascii=False)
# #  ==================== alternativve use ========================

# def extract_notices_from_panels(notice_panels):
#     all_notices = {}

#     for index, panel in enumerate(notice_panels):
#         notice_id = f"notice-{index + 1}"
#         full_text = panel.get("full_notice_text", "").strip()

#         if not full_text:
#             continue

#         extracted_data = extract_data_from_notice(full_text)

#         if extracted_data:
#             all_notices[notice_id] = extracted_data

#     # Save the all_notices dictionary to JSON with notice keys
#     output_path = r"F:\eFaida\scraping-project\data\final.json"

#     with open(output_path, "w", encoding="utf-8") as f:
#         json.dump(all_notices, f, indent=2, ensure_ascii=False)

#     print("✅ Saved as structured JSON with proper 'notice-1', 'notice-2' keys.")



# ============================ code 3 ============================



import openai
import json
from dotenv import load_dotenv
import os

# Load environment variables from .env file
load_dotenv()
openai.api_key = os.getenv('OPENAI_API_KEY')

structured_path = r"F:\eFaida\scraping-project\data\final.json"
failed_path = r"F:\eFaida\scraping-project\data\failed.json"

# Ensure output files exist
for path, default in [(structured_path, {}), (failed_path, [])]:
    if not os.path.exists(path):
        with open(path, "w", encoding="utf-8") as f:
            json.dump(default, f, indent=2)

def extract_data_from_notice(notice_text):
    prompt = f"""
You are a data extraction assistant. Extract the following fields from the provided legal/business notice.

Return the result **strictly** as a valid JSON object with these exact keys:
- notice_date
- publication_name
- location_name
- street_address
- city
- state
- zip_code
- auction_site_used
- count_of_tenants
- all_tenants
- full_notice_text

Format:
{{
  "notice_date": "",
  "publication_name": "",
  "location_name": "",
  "street_address": "",
  "city": "",
  "state": "",
  "zip_code": "",
  "auction_site_used": "",
  "count_of_tenants": 0,
  "all_tenants": [],
  "full_notice_text": ""
}}

Ensure double quotes only and valid JSON output.

Notice:
\"\"\"{notice_text}\"\"\"
"""
    try:
        response = openai.ChatCompletion.create(
            model="gpt-4o-mini",
            messages=[{"role": "user", "content": prompt}],
            temperature=0
        )

        result = response['choices'][0]['message']['content']
        extracted_data = json.loads(result)

        if "full_notice_text" not in extracted_data:
            extracted_data["full_notice_text"] = notice_text.strip()

        return extracted_data

    except json.JSONDecodeError:
        print(f"[ERROR] Failed to parse OpenAI response as JSON:\n{result}")
        return None

    except Exception as e:
        print(f"[EXCEPTION] {str(e)}")
        return None

def extract_notices_from_panels(notice_panels):
    # Load current output so we can resume
    with open(structured_path, "r", encoding="utf-8") as f:
        all_notices = json.load(f)

    with open(failed_path, "r", encoding="utf-8") as f:
        failed_notices = json.load(f)

    for index, panel in enumerate(notice_panels):
        notice_id = f"notice-{index + 1}"

        # Skip already-processed ones
        if notice_id in all_notices:
            print(f"⚠️ Skipping already processed {notice_id}")
            continue

        full_text = panel.get("full_notice_text", "").strip()

        if not full_text:
            print(f"⛔ Empty text for {notice_id}, skipping.")
            continue

        print(f"🔍 Extracting {notice_id}...")

        try:
            data = extract_data_from_notice(full_text)

            if not data or not isinstance(data, dict):
                raise ValueError("Missing or invalid keys")

            # Save immediately to structured file
            all_notices[notice_id] = data
            with open(structured_path, "w", encoding="utf-8") as f:
                json.dump(all_notices, f, indent=2, ensure_ascii=False)
            print(f"✅ Saved {notice_id}")

        except Exception as e:
            fail_record = {
                "notice_id": notice_id,
                "text": full_text,
                "error": str(e)
            }
            failed_notices.append(fail_record)

            with open(failed_path, "w", encoding="utf-8") as f:
                json.dump(failed_notices, f, indent=2, ensure_ascii=False)

            print(f"❌ Failed to extract {notice_id}: {e}")


# ============================ code 4 ============================

# import openai
# import json
# from dotenv import load_dotenv
# import os
# import time

# # Load API key
# load_dotenv()
# openai.api_key = os.getenv('OPENAI_API_KEY')

# def extract_notice_details(notice_text):
#     # Define the prompt to extract the required fields
#     prompt = f"""
#     Extract the following details from the full notice text:
#     - notice_date
#     - publication_name
#     - location_name
#     - street_address
#     - city
#     - state
#     - zip_code
#     - auction_site_used
#     - count_of_tenants
#     - all_tenants
#     - full_notice_text

#     Full notice text:
#     {notice_text}

#     Output in JSON format:
#     {{
#         "notice_date": "",
#         "publication_name": "",
#         "location_name": {{
#             "street_address": "",
#             "city": "",
#             "state": ""
#         }},
#         "zip_code": "",
#         "auction_site_used": "",
#         "count_of_tenants": "",
#         "all_tenants": "",
#         "full_notice_text": ""
#     }}
#     """
    
#     # Call OpenAI model to process the prompt
#     response = openai.Completion.create(
#         engine="gpt-4o-mini",  # You can adjust the model here
#         prompt=prompt,
#         max_tokens=1000,
#         temperature=0.5
#     )
    
#     # Get the output as JSON
#     output = response.choices[0].text.strip()
#     return output

# def process_json_file(input_file, output_file):
#     # Read the input JSON file
#     with open(input_file, 'r') as file:
#         data = json.load(file)
    
#     # Initialize a dictionary to store the extracted data
#     processed_data = {}

#     # Iterate over each notice in the JSON data
#     for notice_id, notice_text_list in data.items():
#         if notice_text_list:
#             # Assuming each entry in the list is the full notice text
#             notice_text = notice_text_list[0]
            
#             # Extract the details using OpenAI API
#             extracted_details = extract_notice_details(notice_text)
            
#             # Store the extracted data in the dictionary
#             processed_data[notice_id] = json.loads(extracted_details)
    
#     # Save the processed data to a new JSON file
#     with open(output_file, 'w') as file:
#         json.dump(processed_data, file, indent=4)

# # Example usage
# input_file = r'F:\eFaida\scraping-project\data\extracted.json'  # Path to your input JSON file
# output_file = r'F:\eFaida\scraping-project\data\extracted_notices.json'  # Path to save the output JSON file

# process_json_file(input_file, output_file)
# print(f"Data has been processed and saved to {output_file}")




