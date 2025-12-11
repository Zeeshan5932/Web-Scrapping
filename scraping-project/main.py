# import json
# import logging
# import os
# from scrapper.scrapper import scrape_notices
# from openai_integration.groq import extract_data_from_notice  # Using Groq integration
# # from openai_integration.openai import extract_data_from_notice  # Using OpenAI integration

# # Configure logging
# logging.basicConfig(
#     level=logging.INFO,  # Use DEBUG for detailed logs
#     format='%(levelname)s:%(message)s'
# )

# def main():
#     url = "https://www.capublicnotice.com/search/query?page=1&size=24&view=list&showExtended=false"
#     search_keywords = "storage"
#     start_date_str = "01/01/2025"
#     end_date_str = "02/28/2025"

#     # Step 1: Scrape and save minimal notices
#     scrape_notices(url, search_keywords, start_date_str, end_date_str)

#     notices_file = r"scraping-project\data\notices_minimal.json"
#     if not os.path.exists(notices_file):
#         logging.error(f"Input file {notices_file} not found. Skipping structured data extraction.")
#         return

#     # Step 2: Load notices from file
#     try:
#         with open(notices_file, "r") as f:
#             notices = json.load(f)
#     except json.JSONDecodeError as e:
#         logging.error(f"Failed to parse {notices_file}: {e}")
#         return

#     structured_results = []

#     # Required keys that must be in model output
#     required_keys = [
#         "notice_date", "publication_name", "location_name", "street_address",
#         "city", "state", "zip_code", "auction_site_used",
#         "count_of_tenants", "all_tenants", "full_notice_text"
#     ]

#     # Step 3: Extract structured data from each notice
#     for idx, notice in enumerate(notices, start=1):
#         full_text = notice.get("Full Text of Notice")
#         if not full_text:
#             logging.warning(f"Notice {idx} missing 'Full Text of Notice'; skipping.")
#             continue

#         try:
#             result = extract_data_from_notice(full_text)
#         except Exception as e:
#             logging.error(f"Extraction failed for notice {idx}: {e}")
#             continue

#         if not isinstance(result, dict):
#             logging.error(f"Invalid data format returned for notice {idx}; skipping.")
#             continue

#         # Validate required keys
#         if not all(key in result for key in required_keys):
#             logging.error(f"Missing required keys in data for notice {idx}: {result}; skipping.")
#             continue

#         logging.debug(f"Extracted data for notice {idx}: {result}")
#         structured_results.append(result)

#     # Step 4: Save structured results
#     output_file = r"scraping-project\data\structured_results.json"
#     try:
#         with open(output_file, "w") as out_f:
#             json.dump(structured_results, out_f, indent=2)
#         logging.info(f"Structured data saved to {output_file}")
#     except Exception as e:
#         logging.error(f"Failed to save structured data: {e}")

# if __name__ == "__main__":
#     main()

# ========================== Alternative Code ==========================

# import json
# import logging
# import os
# from scrapper.scrapper import scrape_notices
# from openai_integration.openai import extract_data_from_notice  # Update if you change the module

# # Configure logging
# logging.basicConfig(
#     level=logging.INFO,  # Use DEBUG for more verbose output
#     format='%(levelname)s: %(message)s'
# )

# def main():
#     url = "https://www.capublicnotice.com/search/query?page=1&size=24&view=list&showExtended=false"
#     search_keywords = "storage"
#     start_date_str = "01/01/2025"
#     end_date_str = "02/28/2025"

#     # Step 1: Scrape and save minimal notices
#     scrape_notices(url, search_keywords, start_date_str, end_date_str)

#     base_data_path = os.path.join("scraping-project", "data")
#     notices_file = os.path.join(base_data_path, "notices_minimal.json")
#     output_file = os.path.join(base_data_path, "structured_results.json")
#     failed_file = os.path.join(base_data_path, "failed_notices.json")

#     if not os.path.exists(notices_file):
#         logging.error(f"Input file {notices_file} not found. Skipping structured data extraction.")
#         return

#     # Step 2: Load notices from file
#     try:
#         with open(notices_file, "r") as f:
#             notices = json.load(f)
#     except json.JSONDecodeError as e:
#         logging.error(f"Failed to parse {notices_file}: {e}")
#         return

#     structured_results = []
#     failed_notices = []

#     required_keys = [
#         "notice_date", "publication_name", "location_name", "street_address",
#         "city", "state", "zip_code", "auction_site_used",
#         "count_of_tenants", "all_tenants", "full_notice_text"
#     ]

#     # Step 3: Extract structured data from each notice
#     for idx, notice in enumerate(notices, start=1):
#         logging.info(f"Processing notice {idx} of {len(notices)}")

#         full_text = notice.get("Full Text of Notice")
#         if not full_text:
#             logging.warning(f"Notice {idx} missing 'Full Text of Notice'; skipping.")
#             continue

#         try:
#             result = extract_data_from_notice(full_text)

#             # Retry once if it fails or missing keys
#             if not result or not all(key in result for key in required_keys):
#                 logging.warning(f"Initial extraction failed or missing keys for notice {idx}, retrying...")
#                 result = extract_data_from_notice(full_text)

#         except Exception as e:
#             logging.error(f"Extraction failed for notice {idx}: {e}")
#             failed_notices.append({
#                 "index": idx,
#                 "text": full_text,
#                 "error": str(e)
#             })
#             continue

#         if not isinstance(result, dict) or not all(key in result for key in required_keys):
#             logging.error(f"Missing or invalid keys in data for notice {idx}")
#             failed_notices.append({
#                 "index": idx,
#                 "text": full_text,
#                 "response": result,
#                 "error": "Missing or invalid keys"
#             })
#             continue

#         # # Optional: add original index or metadata to track it back
#         # result["source_index"] = idx
#         # result["original_notice_excerpt"] = full_text[:200]

#         structured_results.append(result)

#     # Step 4: Save structured results
#     try:
#         with open(output_file, "w") as out_f:
#             json.dump(structured_results, out_f, indent=2)
#         logging.info(f"✅ Structured data saved to {output_file}")
#     except Exception as e:
#         logging.error(f"❌ Failed to save structured data: {e}")

#     # Step 5: Save failed extractions (if any)
#     if failed_notices:
#         try:
#             with open(failed_file, "w") as f:
#                 json.dump(failed_notices, f, indent=2)
#             logging.warning(f"⚠️ {len(failed_notices)} notices failed and saved to {failed_file}")
#         except Exception as e:
#             logging.error(f"❌ Failed to save failed notices: {e}")

# if __name__ == "__main__":
#     main()

# ========================== Alternative Code ==========================


import json
import logging
import os
from scrapper.scrapper import scrape_notices
from openai_integration.openai_integration import extract_data_from_notice  # Update if you change the module

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(levelname)s: %(message)s'
)

def main():
    url = "https://www.capublicnotice.com/search/query?page=1&size=24&view=list&showExtended=false"
    search_keywords = "storage"
    start_date_str = "01/01/2025"
    end_date_str = "02/28/2025"

    # Step 1: Scrape and save minimal notices
    scrape_notices(url, search_keywords, start_date_str, end_date_str)

    base_data_path = os.path.join("scraping-project", "data")
    notices_file = os.path.join(base_data_path, "notices_minimal.json")
    output_file = os.path.join(base_data_path, "structured_results.json")

    if not os.path.exists(notices_file):
        logging.error(f"Input file {notices_file} not found. Skipping structured data extraction.")
        return

    # Step 2: Load notices from file
    try:
        with open(notices_file, "r") as f:
            notices = json.load(f)
    except json.JSONDecodeError as e:
        logging.error(f"Failed to parse {notices_file}: {e}")
        return

    structured_results = {}  # Now a dict, not a list
    failed_notices = []

    required_keys = [
        "notice_date", "publication_name", "location_name", "street_address",
        "city", "state", "zip_code", "auction_site_used",
        "count_of_tenants", "all_tenants", "full_notice_text"
    ]

    # Step 3: Extract structured data from each notice
    for idx, notice in enumerate(notices, start=1):
        logging.info(f"Processing notice {idx} of {len(notices)}")

        full_text = notice.get("Full Text of Notice")
        if not full_text:
            logging.warning(f"Notice {idx} missing 'Full Text of Notice'; skipping.")
            continue

        try:
            result = extract_data_from_notice(full_text)

            if not result or not all(key in result for key in required_keys):
                logging.warning(f"Initial extraction failed or missing keys for notice {idx}, retrying...")
                result = extract_data_from_notice(full_text)

        except Exception as e:
            logging.error(f"Extraction failed for notice {idx}: {e}")
            failed_notices.append({
                "index": idx,
                "text": full_text,
                "error": str(e)
            })
            continue

        if not isinstance(result, dict) or not all(key in result for key in required_keys):
            logging.error(f"Missing or invalid keys in data for notice {idx}")
            failed_notices.append({
                "index": idx,
                "text": full_text,
                "response": result,
                "error": "Missing or invalid keys"
            })
            continue

        notice_key = f"notice-{idx}"
        structured_results[notice_key] = result

    # Step 4: Save structured results
    try:
        with open(output_file, "w") as out_f:
            json.dump(structured_results, out_f, indent=2)
        logging.info(f"✅ Structured data saved to {output_file}")
    except Exception as e:
        logging.error(f"❌ Failed to save structured data: {e}")

    # # Step 5: Save failed extractions (if any)
    # if failed_notices:
    #     try:
    #         with open(failed_file, "w") as f:
    #             json.dump(failed_notices, f, indent=2)
    #         logging.warning(f"⚠️ {len(failed_notices)} notices failed and saved to {failed_file}")
    #     except Exception as e:
    #         logging.error(f"❌ Failed to save failed notices: {e}")

if __name__ == "__main__":
    main()



# ======================= Alternative Code =======================

# import json
# import logging
# import os
# import jsonlines  # For efficient appending to JSONL (you need to install the package with `pip install jsonlines`)
# from scrapper.scrapper import scrape_notices
# from openai_integration.openai import extract_data_from_notice  # Update if you change the module

# # Configure logging
# logging.basicConfig(
#     level=logging.INFO,
#     format='%(levelname)s: %(message)s'
# )

# def main():
#     url = "https://www.capublicnotice.com/search/query?page=1&size=24&view=list&showExtended=false"
#     search_keywords = "storage"
#     start_date_str = "01/01/2025"
#     end_date_str = "02/28/2025"

#     # Step 1: Scrape and save minimal notices
#     scrape_notices(url, search_keywords, start_date_str, end_date_str)

#     base_data_path = os.path.join("scraping-project", "data")
#     notices_file = os.path.join(base_data_path, "notices_minimal.json")
#     output_file = os.path.join(base_data_path, "structured_results.jsonl")  # Changed to JSONL
#     failed_file = os.path.join(base_data_path, "failed_notices.jsonl")  # Changed to JSONL

#     if not os.path.exists(notices_file):
#         logging.error(f"Input file {notices_file} not found. Skipping structured data extraction.")
#         return

#     # Step 2: Load notices from file
#     try:
#         with open(notices_file, "r") as f:
#             notices = json.load(f)
#     except json.JSONDecodeError as e:
#         logging.error(f"Failed to parse {notices_file}: {e}")
#         return

#     failed_notices = []

#     required_keys = [
#         "notice_date", "publication_name", "location_name", "street_address",
#         "city", "state", "zip_code", "auction_site_used",
#         "count_of_tenants", "all_tenants", "full_notice_text"
#     ]

#     # Step 3: Extract structured data from each notice
#     for idx, notice in enumerate(notices, start=1):
#         logging.info(f"Processing notice {idx} of {len(notices)}")

#         full_text = notice.get("Full Text of Notice")
#         if not full_text:
#             logging.warning(f"Notice {idx} missing 'Full Text of Notice'; skipping.")
#             continue

#         try:
#             result = extract_data_from_notice(full_text)

#             if not result or not all(key in result for key in required_keys):
#                 logging.warning(f"Initial extraction failed or missing keys for notice {idx}, retrying...")
#                 result = extract_data_from_notice(full_text)

#         except Exception as e:
#             logging.error(f"Extraction failed for notice {idx}: {e}")
#             failed_notices.append({
#                 "index": idx,
#                 "text": full_text,
#                 "error": str(e)
#             })
#             continue

#         if not isinstance(result, dict) or not all(key in result for key in required_keys):
#             logging.error(f"Missing or invalid keys in data for notice {idx}")
#             failed_notices.append({
#                 "index": idx,
#                 "text": full_text,
#                 "response": result,
#                 "error": "Missing or invalid keys"
#             })
#             continue

#         # Save structured data immediately to JSONL
#         with jsonlines.open(output_file, mode='a') as writer:
#             writer.write({"notice_id": f"notice-{idx}", **result})

#         logging.info(f"✅ Saved notice-{idx}")

#     # # Step 4: Save failed extractions (if any)
#     # if failed_notices:
#     #     try:
#     #         with jsonlines.open(failed_file, mode='a') as writer:
#     #             for failed_notice in failed_notices:
#     #                 writer.write(failed_notice)
#     #         logging.warning(f"⚠️ {len(failed_notices)} notices failed and saved to {failed_file}")
#     #     except Exception as e:
#     #         logging.error(f"❌ Failed to save failed notices: {e}")

# if __name__ == "__main__":
#     main()
