import gspread
from oauth2client.service_account import ServiceAccountCredentials
import datetime
import time

# === CONSTANTS ===
BATCH_SIZE = 500
SHEET_NAME = "Danish"
OUTPUT_SHEET_NAME = "Combined Report"
CREDENTIALS_FILE = "credentials/credentials.json"

# === AUTHENTICATION ===
def authenticate_google_sheets():
    scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
    creds = ServiceAccountCredentials.from_json_keyfile_name(CREDENTIALS_FILE, scope)
    return gspread.authorize(creds)

# === DATE FORMATTING ===
def format_date(raw_date):
    for fmt in ("%Y-%m-%d", "%m/%d/%Y"):
        try:
            parsed_date = datetime.datetime.strptime(raw_date.strip(), fmt)
            return parsed_date.strftime("%-m/%-d/%y")  # Linux/Mac: %-m, Windows: %#m
        except:
            continue
    return raw_date.strip()

# === LOAD SHEET DATA ===
def get_data_from_sheet(client, sheet_name):
    sheet = client.open(SHEET_NAME).worksheet(sheet_name)
    data = sheet.get_all_values()
    return data[0], data[1:]  # header, rows

# === FIND CELL VALUE ===
def find_matching_data(sheet_data, sheet_headers, website, date_key):
    try:
        for row in sheet_data:
            if len(row) > 1 and row[1].strip().lower() == website.strip().lower():
                for col_idx, header in enumerate(sheet_headers):
                    if header.strip() == date_key.strip():
                        return row[col_idx].strip() if col_idx < len(row) and row[col_idx].strip() != "" else None
        return None
    except Exception as e:
        print(f"⚠️ Error finding data for {website} on {date_key}: {e}")
        return None

# === GET METRICS FROM PRIORITY SHEET ===
def get_data_from_priority_sheet(all_data, all_headers, website, date):
    priority_sheets = ["Traffic Average", "Traffic Monthly", "DR", "RD", "Keywords"]
    for sheet_name in priority_sheets:
        if sheet_name in all_data:
            result = find_matching_data(all_data[sheet_name], all_headers[sheet_name], website, date)
            if result and result != "0":
                return (
                    find_matching_data(all_data["Traffic Average"], all_headers["Traffic Average"], website, date) or 0,
                    find_matching_data(all_data["Traffic Monthly"], all_headers["Traffic Monthly"], website, date) or 0,
                    find_matching_data(all_data["DR"], all_headers["DR"], website, date) or 0,
                    find_matching_data(all_data["RD"], all_headers["RD"], website, date) or 0,
                    find_matching_data(all_data["Keywords"], all_headers["Keywords"], website, date) or 0,
                    sheet_name
                )
    return 0, 0, 0, 0, 0, "No Data"

# === MAIN FUNCTION ===
def generate_filtered_combined_report():
    print("🚀 Processing started...")

    client = authenticate_google_sheets()

    # Load and format dates
    print("📅 Loading dates...")
    correct_dates_raw = client.open(SHEET_NAME).worksheet("Correct Dates ").col_values(1)
    correct_dates = [format_date(d) for d in correct_dates_raw if d.strip()]
    print(f"✅ Dates loaded: {len(correct_dates)}")

    # Load data from all input sheets
    sheet_names = ["Traffic Average", "Traffic Monthly", "DR", "RD", "Keywords"]
    data = {}
    headers = {}

    print("📊 Loading sheet data...")
    for sheet_name in sheet_names:
        header, rows = get_data_from_sheet(client, sheet_name)
        data[sheet_name] = rows
        headers[sheet_name] = header
        print(f"✅ {sheet_name}: {len(rows)} rows")

    # Get unique websites
    websites = []
    website_types = {}
    for row in data["Traffic Average"]:
        if len(row) > 1:
            site = row[1].strip()
            if site and site not in websites:
                websites.append(site)
                website_types[site] = row[2].strip() if len(row) > 2 else ""

    print(f"🌐 Total websites found: {len(websites)}")

    # === USER CONTINUE PROMPT ===
    user_input = input("\n🔄 Press Enter to continue with data processing or type 'exit' to stop: ")
    if user_input.lower() == "exit":
        print("❌ Cancelled by user.")
        return

    # Prepare output sheet
    try:
        output_sheet = client.open(SHEET_NAME).worksheet(OUTPUT_SHEET_NAME)
        output_sheet.clear()
    except gspread.exceptions.WorksheetNotFound:
        output_sheet = client.open(SHEET_NAME).add_worksheet(title=OUTPUT_SHEET_NAME, rows="1000", cols="10")

    # Add column headers
    output_sheet.append_row(["#", "Website", "Type", "Date", "Traffic Average", "Traffic Monthly", "DR", "RD", "Keywords"])

    all_rows_to_write = []
    row_counter = 1
    processed_count = 0
    total_combinations = len(websites) * len(correct_dates)

    print("🔁 Starting data processing...\n")

    for website in websites:
        website_type = website_types.get(website, "")
        for date in correct_dates:
            processed_count += 1

            # Get data using fallback logic
            traffic_avg, traffic_monthly, dr_val, rd_val, keywords_val, source = get_data_from_priority_sheet(
                data, headers, website, date
            )

            if traffic_avg == 0:
                continue  # Skip if no valid traffic_avg

            row = [
                row_counter,
                website,
                website_type,
                date,
                traffic_avg,
                traffic_monthly,
                dr_val,
                rd_val,
                keywords_val
            ]

            all_rows_to_write.append(row)
            row_counter += 1

            # Write in batches and delay
            if len(all_rows_to_write) >= BATCH_SIZE:
                print(f"📈 Processed {processed_count}/{total_combinations} combinations...")
                print(f"💾 Writing batch of {len(all_rows_to_write)} rows...")
                output_sheet.append_rows(all_rows_to_write)
                all_rows_to_write = []
                print("⏳ Waiting 3 seconds to avoid quota...")
                time.sleep(3)

    # Write any remaining rows
    if all_rows_to_write:
        print(f"💾 Writing final {len(all_rows_to_write)} rows...")
        output_sheet.append_rows(all_rows_to_write)

    print("\n✅ Done!")
    print(f"🧾 Total rows saved: {row_counter - 1}")
    print(f"🌐 Websites: {len(websites)}")
    print(f"📅 Dates: {len(correct_dates)}")

# === EXECUTION POINT ===
if __name__ == "__main__":
    generate_filtered_combined_report()
