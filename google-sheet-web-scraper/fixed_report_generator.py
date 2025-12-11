import gspread
from oauth2client.service_account import ServiceAccountCredentials
import datetime
import time
import json
import os

# Constants
BATCH_SIZE = 500
SHEET_NAME = "Danish"                     # ← your spreadsheet name
OUTPUT_SHEET_NAME = "Combined Report"
CREDENTIALS_FILE = "credentials/credentials.json"
PROGRESS_FILE = "progress.json"
PRIORITY_SHEETS = ["Traffic Average", "Traffic Monthly", "DR", "RD", "Keywords"]

def authenticate_google_sheets():
    """Authenticate with Google Sheets API."""
    scope = ["https://spreadsheets.google.com/feeds",
             "https://www.googleapis.com/auth/drive"]
    creds = ServiceAccountCredentials.from_json_keyfile_name(CREDENTIALS_FILE, scope)
    return gspread.authorize(creds)

def format_date(raw_date):
    """Normalize any raw_date string into M/D/YY (no leading zeros)."""
    if not raw_date:
        return ""
        
    # Try to clean the input
    cleaned = raw_date.strip() if isinstance(raw_date, str) else str(raw_date)
        
    # Try common date formats
    for fmt in ("%Y-%m-%d", "%m/%d/%Y", "%m/%d/%y"):
        try:
            dt = datetime.datetime.strptime(cleaned, fmt)
            return f"{dt.month}/{dt.day}/{dt.year % 100}"
        except:
            continue
            
    # If still here, try to extract date components from the string
    if '/' in cleaned:
        parts = cleaned.split('/')
        if len(parts) == 3:
            try:
                month = int(parts[0])
                day = int(parts[1])
                year = int(parts[2]) if len(parts[2]) > 2 else int(parts[2]) + 2000
                return f"{month}/{day}/{year % 100}"
            except:
                pass
    
    # Return as is if all else fails
    return cleaned

def date_exists_in_header(headers, date_key):
    """Return True if date_key (formatted) is one of the column headers."""
    return date_key in headers

def has_data_for_date(data, headers, row_idx, date_key):
    """Return True if the cell at row_idx×date_key contains non-blank data."""
    if date_key in headers:
        c = headers[date_key]
        if row_idx < len(data) and c < len(data[row_idx]):
            v = data[row_idx][c]
            # Consider any non-empty value as valid data (including "0")
            return bool(v) and str(v).strip() != ""
    return False

def get_value(data, headers, row_idx, date_key):
    """Fetch the actual cell value or return 0 if blank/missing."""
    if date_key in headers:
        c = headers[date_key]
        if row_idx < len(data) and c < len(data[row_idx]):
            v = data[row_idx][c]
            if v not in ("", None):
                # Keep the original value format (string or number)
                return v
    return 0

def save_progress(row_idx, date_idx):
    """Persist where we left off so we can resume later."""
    with open(PROGRESS_FILE, "w") as f:
        json.dump({"last_row_index": row_idx, "last_date_index": date_idx}, f)
    print(f"💾 Progress saved at row {row_idx}, date index {date_idx}")

def load_progress():
    """Load saved progress or start fresh."""
    if os.path.exists(PROGRESS_FILE):
        try:
            with open(PROGRESS_FILE) as f:
                p = json.load(f)
                return p.get("last_row_index", 1), p.get("last_date_index", 0)
        except:
            pass
    return 1, 0

def clear_progress():
    """Remove the progress file when done."""
    if os.path.exists(PROGRESS_FILE):
        os.remove(PROGRESS_FILE)

def generate_filtered_combined_report():
    print("🚀 Processing started...")
    client = authenticate_google_sheets()
    ss = client.open(SHEET_NAME)

    # 1) Load and normalize correct dates
    print("📅 Loading correct dates...")
    cd_ws = ss.worksheet("CORRECT DATES")
    raw_dates = [d for d in cd_ws.col_values(1) if d.strip()]
    correct_dates = [format_date(d) for d in raw_dates]
    
    print(f"✅ Found {len(correct_dates)} dates")
    print(f"📅 Sample raw dates: {raw_dates[:3]}")
    print(f"📅 Sample formatted dates: {correct_dates[:3]}")

    # 2) Load each priority sheet and build header→index maps
    print("📊 Loading all sheet data...")
    data_sheets = {}
    header_indexes = {}
    date_headers_found = {}
    
    for name in PRIORITY_SHEETS:
        print(f"   Loading {name}...")
        ws = ss.worksheet(name)
        vals = ws.get_all_values()
        data_sheets[name] = vals
        hdr = vals[0] if vals else []
        
        # Create two maps: one for exact matching and one for formatted dates
        exact_headers = {}
        formatted_headers = {}
        date_headers_found[name] = []
        
        for i in range(len(hdr)):
            if hdr[i].strip():
                # Store the exact header text
                exact_headers[hdr[i].strip()] = i
                
                # Also try to format it as a date if it looks like one
                if any(c in hdr[i] for c in ['/', '-']):
                    formatted = format_date(hdr[i])
                    formatted_headers[formatted] = i
                    date_headers_found[name].append(formatted)
        
        # Combine both maps, with formatted dates taking precedence
        all_headers = {**exact_headers, **formatted_headers}
        header_indexes[name] = all_headers
        
        print(f"   • {name}: {len(vals)} rows, {len(all_headers)} headers")
        if date_headers_found[name]:
            print(f"     Found date headers: {date_headers_found[name][:3]}{'...' if len(date_headers_found[name]) > 3 else ''}")

    # 3) Prepare output sheet
    print("📝 Setting up output sheet...")
    try:
        out_ws = ss.worksheet(OUTPUT_SHEET_NAME)
        out_ws.clear()
    except gspread.exceptions.WorksheetNotFound:
        out_ws = ss.add_worksheet(title=OUTPUT_SHEET_NAME, rows="10000", cols="10")
    out_ws.append_row(["#", "Website", "Type", "Date",
                      "Traffic Average", "Traffic Monthly",
                      "DR", "RD", "Keywords"])

    # 4) Resume or start from scratch
    start_row, start_date_i = load_progress()
    total_rows = len(data_sheets["Traffic Average"])
    print(f"🔄 Starting processing at row {start_row}, date index {start_date_i}")
    print(f"📊 Total rows to process: {total_rows}")
    
    # Confirm before proceeding
    user_input = input("Press Enter to continue or type 'exit' to cancel: ")
    if user_input.lower() == 'exit':
        print("❌ Process cancelled by user")
        return

    # Prepare for batch processing
    batch = []
    written = 0
    
    print("🔄 Starting data extraction...")

    # 5) Main extraction loops
    for i in range(start_row, total_rows):
        # Skip header row
        if i == 0:
            continue
            
        row = data_sheets["Traffic Average"][i]
        if len(row) < 2 or not row[1].strip():
            continue
            
        # Get website information
        num = row[0] or i
        site = row[1].strip()
        typ = row[2].strip() if len(row) > 2 and row[2] else ""
        
        if i % 10 == 0:
            print(f"Processing website: {site} (row {i}/{total_rows-1})")

        # Process each date for this website
        for j in range(start_date_i if i == start_row else 0, len(correct_dates)):
            date = correct_dates[j]
            
            # Implementation of your specific logic:
            
            # 1. Check if date exists in any sheet header
            date_exists = False
            for sheet_name in PRIORITY_SHEETS:
                if date_exists_in_header(header_indexes[sheet_name], date):
                    date_exists = True
                    break
            
            if not date_exists:
                continue  # Skip dates not found in any sheet
                
            # 2. Check for data in Traffic Average first
            traffic_has_data = has_data_for_date(data_sheets["Traffic Average"], 
                                               header_indexes["Traffic Average"], 
                                               i, date)
            
            # 3. Extract data from all sheets
            ta = get_value(data_sheets["Traffic Average"], header_indexes["Traffic Average"], i, date)
            tm = get_value(data_sheets["Traffic Monthly"], header_indexes["Traffic Monthly"], i, date)
            dr = get_value(data_sheets["DR"], header_indexes["DR"], i, date)
            rd = get_value(data_sheets["RD"], header_indexes["RD"], i, date)
            kw = get_value(data_sheets["Keywords"], header_indexes["Keywords"], i, date)
            
            # 4. Check if we have any meaningful data
            has_any_data = any(str(v).strip() not in ["", "0"] for v in [ta, tm, dr, rd, kw])
            
            # Only include rows with data or where Traffic Average has data
            if traffic_has_data or has_any_data:
                # Add row to batch
                batch.append([num, site, typ, date, ta, tm, dr, rd, kw])
                written += 1
                
                # Show progress periodically
                if written % 50 == 0:
                    print(f"Found {written} rows with data...")
            
            # Check if batch is ready to write
            if len(batch) >= BATCH_SIZE:
                print(f"⏸️ Writing batch of {len(batch)} rows...")
                out_ws.append_rows(batch)
                batch = []
                
                # Save progress before pausing
                save_progress(i, j + 1)
                print(f"⏸️ Pausing after processing {written} rows. Run again to continue.")
                return  # Stop and allow resuming later
        
        # Reset date index for next row
        start_date_i = 0

    # Write any remaining rows
    if batch:
        print(f"💾 Writing final batch of {len(batch)} rows...")
        out_ws.append_rows(batch)
    
    # Clean up progress file
    clear_progress()
    print(f"✅ All done! {written} rows processed and saved.")

if __name__ == "__main__":
    generate_filtered_combined_report()
