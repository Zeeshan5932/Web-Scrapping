"""
Combined Report Generator Utilities
==================================

Simple utility functions for managing the combined report generation process.
"""

import os
from datetime import datetime
from combined_report_generator import CombinedReportGenerator
from config import GOOGLE_SHEET_CONFIG

# Import batch generator
try:
    from batch_report_generator import generate_proper_combined_report
    BATCH_GENERATOR_AVAILABLE = True
except ImportError:
    BATCH_GENERATOR_AVAILABLE = False


def check_status():
    """Check if the report generator is running or completed"""
    print("Combined Report Generator - Status Check")
    print("=" * 50)
    
    try:
        credentials_path = GOOGLE_SHEET_CONFIG['credentials_path']
        sheet_url = GOOGLE_SHEET_CONFIG['sheet_url']
        
        generator = CombinedReportGenerator(credentials_path)
        generator.open_spreadsheet(sheet_url)
        
        # Check if Combined Report sheet exists
        try:
            combined_sheet = generator.spreadsheet.worksheet("Combined Report")
            row_count = len(combined_sheet.get_all_values())
            
            if row_count > 1:  # More than just header
                print("✅ Report generation COMPLETED")
                print(f"   Combined Report sheet exists with {row_count-1} data rows")
                print(f"   Last updated: Check your Google Sheet")
            else:
                print("📝 Combined Report sheet exists but is empty")
                print("   Report generation may be in progress or failed")
        except:
            print("⏳ No Combined Report sheet found")
            print("   Report generation has not started or completed yet")
        
    except Exception as e:
        print(f"❌ Error checking status: {e}")


def start_batch_generation():
    """Start the batch report generation process (gspread version)"""
    print("Batch Report Generator - Start Processing")
    print("=" * 50)
    
    if not BATCH_GENERATOR_AVAILABLE:
        print("❌ Batch generator not available")
        print("   Please ensure batch_report_generator.py is in the same directory")
        return
    
    try:
        print("🚀 Starting batch report generation...")
        print("   This uses the gspread version with batch processing")
        print("   Note: You need to configure credentials and sheet name in batch_report_generator.py")
        print("   Please wait while processing completes...")
        print()
        
        # Run the batch generator
        generate_proper_combined_report()
        
        print("✅ Batch report generation completed!")
        print("   Check your Google Sheet for the 'Combined Report' tab")
            
    except Exception as e:
        print(f"❌ Error during batch generation: {e}")
        print("   Make sure to configure the credentials and sheet name in batch_report_generator.py")


def start_generation():
    """Start the report generation process"""
    print("Combined Report Generator - Start Processing")
    print("=" * 50)
    
    try:
        credentials_path = GOOGLE_SHEET_CONFIG['credentials_path']
        sheet_url = GOOGLE_SHEET_CONFIG['sheet_url']
        
        print("🚀 Starting report generation...")
        print("   This will process all data in one go")
        print("   Please wait while processing completes...")
        print()
        
        generator = CombinedReportGenerator(credentials_path)
        
        # Generate the report
        success = generator.generate_combined_report(sheet_url)
        
        if success:
            print("✅ Report generation COMPLETED successfully!")
            print("   Check your Google Sheet for the 'Combined Report' tab")
        else:
            print("❌ Report generation failed")
            
    except Exception as e:
        print(f"❌ Error during generation: {e}")


def preview_data():
    """Preview the data that will be processed"""
    print("Combined Report Generator - Data Preview")
    print("=" * 50)
    
    try:
        credentials_path = GOOGLE_SHEET_CONFIG['credentials_path']
        sheet_url = GOOGLE_SHEET_CONFIG['sheet_url']
        
        generator = CombinedReportGenerator(credentials_path)
        generator.open_spreadsheet(sheet_url)
        generator.load_correct_dates()
        generator.load_data_sheets()
        
        print(f"📋 Spreadsheet: {generator.spreadsheet.title}")
        print()
        
        print(f"📅 Found {len(generator.correct_dates)} dates:")
        for i, date in enumerate(generator.correct_dates[:5]):  # Show first 5
            formatted = generator.format_date(date)
            print(f"   {i+1}. {date} → {formatted}")
        if len(generator.correct_dates) > 5:
            print(f"   ... and {len(generator.correct_dates) - 5} more dates")
        print()
        
        print(f"📊 Data Sheets:")
        total_websites = 0
        for sheet_name in generator.sheet_names:
            if sheet_name in generator.data_sheets:
                rows = len(generator.data_sheets[sheet_name]) - 1  # Exclude header
                print(f"   ✅ {sheet_name}: {rows} websites")
                if sheet_name == "Traffic Average":
                    total_websites = rows
            else:
                print(f"   ❌ {sheet_name}: Not found")
        print()
        
        if total_websites > 0:
            total_combinations = total_websites * len(generator.correct_dates)
            print(f"🔢 Total processing:")
            print(f"   {total_websites} websites × {len(generator.correct_dates)} dates = {total_combinations:,} rows will be created")
        
    except Exception as e:
        print(f"❌ Error previewing data: {e}")


def main():
    """Main utility menu"""
    while True:
        print("\nCombined Report Generator - Simple Utilities")
        print("=" * 45)
        print("1. Check Status")
        print("2. Preview Data") 
        print("3. Start Generation (Google Sheets API)")
        if BATCH_GENERATOR_AVAILABLE:
            print("4. Start Batch Generation (gspread)")
            print("5. Exit")
        else:
            print("4. Exit")
        print()
        
        max_choice = 5 if BATCH_GENERATOR_AVAILABLE else 4
        choice = input(f"Select an option (1-{max_choice}): ").strip()
        
        if choice == '1':
            check_status()
        elif choice == '2':
            preview_data()
        elif choice == '3':
            start_generation()
        elif choice == '4' and BATCH_GENERATOR_AVAILABLE:
            start_batch_generation()
        elif choice == '5' and BATCH_GENERATOR_AVAILABLE:
            print("Goodbye!")
            break
        elif choice == '4' and not BATCH_GENERATOR_AVAILABLE:
            print("Goodbye!")
            break
        else:
            print(f"Invalid choice. Please select 1-{max_choice}.")
        
        print()
        input("Press Enter to continue...")


if __name__ == "__main__":
    main()
