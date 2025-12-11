# import json
# import os
# from dotenv import load_dotenv
# import requests  # Assuming you'll make HTTP requests to the Groq API

# # Load environment variables from .env file
# load_dotenv()

# # Set the Groq API key from the .env file
# groq_api_key = os.getenv('GROQ_API_KEY')
# groq_api_url = 'https://api.groq.com/openai/v1/chat/completions'  # Replace with Groq's actual endpoint

# def extract_data_from_notice(notice_text):
#     prompt = f"""
#     Extract the following fields from the notice below and return the result strictly in valid JSON format with keys:
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

#     Notice: \"\"\"{notice_text}\"\"\"
#     """

#     payload = {
#         "model": "llama-guard-3-8b",  # The specific model you're using, replace if necessary
#         "prompt": prompt,
#         "temperature": 0.5,
#         "max_tokens": 500
#     }

#     headers = {
#         'Authorization': f'Bearer {groq_api_key}',
#         'Content-Type': 'application/json'
#     }

#     # Make the API request to Groq's endpoint
#     response = requests.post(groq_api_url, json=payload, headers=headers)

#     # Check if the API response is successful (HTTP 200)
#     if response.status_code == 200:
#         try:
#             result = response.json()

#             # Groq might return OpenAI-style responses, check the structure
#             model_response = result.get('choices', [{}])[0].get('text', '')

#             # Try to parse the response from Groq which is expected to be a valid JSON string
#             extracted_data = json.loads(model_response)

#             # Ensure all required keys exist in the response (set default to empty string if missing)
#             required_keys = [
#                 "notice_date", "publication_name", "location_name", "street_address",
#                 "city", "state", "zip_code", "auction_site_used",
#                 "count_of_tenants", "all_tenants", "full_notice_text"
#             ]
#             for key in required_keys:
#                 extracted_data.setdefault(key, "")

#             return extracted_data

#         except json.JSONDecodeError as e:
#             # Print the error message and the raw response for debugging
#             print(f"JSON decode error: {e}")
#             print("Raw model response:\n", result)  # Print the raw response here
#             return None
#     else:
#         # If the response code is not 200, log the status code and response
#         print(f"Failed to get response from Groq API. Status code: {response.status_code}")
#         print("Raw response:\n", response.text)  # Print the raw response here
#         return None



import json
import logging
import os
import requests
import re
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Set the Groq API key from the .env file
groq_api_key = os.getenv('GROQ_API_KEY')
groq_api_url = "https://api.groq.com/openai/v1/chat/completions"

# Required keys for validation
REQUIRED_KEYS = {
    "notice_date",
    "publication_name",
    "location_name",
    "street_address",
    "city",
    "state",
    "zip_code",
    "auction_site_used",
    "count_of_tenants",
    "all_tenants",
    "full_notice_text"
}

# Extract JSON from raw model response
def extract_json_from_text(text):
    # First try to extract from markdown-style block
    match = re.search(r"```json\s*({.*?})\s*```", text, re.DOTALL)
    if not match:
        # Fallback to raw JSON inside text
        match = re.search(r"\{.*\}", text, re.DOTALL)
    
    if match:
        try:
            return json.loads(match.group())
        except json.JSONDecodeError as e:
            logging.error(f"❌ JSON decoding error: {e}")
            return None
    else:
        logging.warning("⚠️ No JSON block found in response.")
        return None

# Clean the tenant count from list or comma-separated string
def clean_tenant_count(tenants):
    try:
        if isinstance(tenants, list):
            return len(tenants)
        elif isinstance(tenants, str):
            tenant_list = [t.strip() for t in tenants.split(",") if t.strip()]
            return len(tenant_list)
        else:
            return 0
    except Exception as e:
        logging.error(f"Error cleaning tenant count: {e}")
        return 0

# Extract structured data using Groq API
def extract_data_from_notice(notice_text, model="llama3-8b-8192"):
    headers = {
        "Authorization": f"Bearer {groq_api_key}",
        "Content-Type": "application/json"
    }

    prompt_text = (
        "Extract the following fields from the legal notice below. "
        "Respond ONLY with valid JSON (no extra text or explanation). "
        "Required fields:\n"
        "- notice_date\n"
        "- publication_name\n"
        "- location_name\n"
        "- street_address\n"
        "- city\n"
        "- state\n"
        "- zip_code\n"
        "- auction_site_used\n"
        "- count_of_tenants\n"
        "- all_tenants (as a list of full names)\n\n"
        "Legal Notice:\n" + notice_text
    )

    payload = {
        "model": model,
        "messages": [
            {
                "role": "system",
                "content": (
                    "You are a helpful assistant that extracts structured data from legal notices. "
                    "Return ONLY valid JSON. No explanation, no markdown, no extra formatting. "
                    "Ensure all required fields are present. Strings should be in double quotes."
                )
            },
            {
                "role": "user",
                "content": prompt_text
            }
        ],
        "temperature": 0.2,
        "max_tokens": 1000
    }

    response = requests.post(groq_api_url, headers=headers, json=payload)

    if response.status_code == 200:
        try:
            response_json = response.json()
            content = response_json["choices"][0]["message"]["content"]
            logging.debug(f"Model raw response:\n{content}")  # Log raw content for debugging

            result = extract_json_from_text(content)

            if not result:
                logging.error("❌ Invalid JSON structure returned; skipping.")
                return None

            # Add full_notice_text if missing
            result["full_notice_text"] = notice_text

            # Ensure count_of_tenants is correct
            result["count_of_tenants"] = clean_tenant_count(result.get("all_tenants", []))

            # Check required fields
            missing_keys = REQUIRED_KEYS - result.keys()
            if missing_keys:
                logging.error(f"❌ Missing required keys: {missing_keys}; skipping.")
                return None

            return result

        except Exception as e:
            logging.error(f"❌ Error parsing Groq response: {e}")
            return None
    else:
        logging.error(f"❌ Groq API request failed. Status code: {response.status_code}")
        logging.error("Raw response:\n" + response.text)
        return None



