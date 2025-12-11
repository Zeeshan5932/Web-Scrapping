"""
Google Sheets Combined Report Generator (Python version of Apps Script)
=====================================================================

This script replicates the functionality of the Google Apps Script that generates
a combined report from multiple sheets.

Features:
- Processes data from multiple sheets: Traffic Average, Traffic Monthly, DR, RD, Keywords
- Uses dates from CORRECT DATES sheet
- Generates combined report with all data combinations
- Direct processing without batch limits - processes all data in one run
- Error handling and logging
"""

import os
import json
import time
from datetime import datetime
from typing import List, Dict, Any, Optional, Tuple
import logging

# Google Sheets
import gspread
from google.oauth2.service_account import Credentials

# Data handling
import pandas as pd

# Import configuration
from config import GOOGLE_SHEET_CONFIG

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('logs/combined_report_generator.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)


class CombinedReportGenerator:
    """
    Python equivalent of the Google Apps Script for generating combined reports
    """
    
    def __init__(self, credentials_path: str):
        """Initialize the report generator"""
        self.credentials_path = credentials_path
        self.client = None
        self.spreadsheet = None
        
        # Sheet names to process
        self.sheet_names = ["Traffic Average", "Traffic Monthly", "DR", "RD", "Keywords"]
        self.correct_dates_sheet_name = "CORRECT DATES"
        self.output_sheet_name = "Combined Report"
        
        # Data storage
        self.data_sheets = {}
        self.header_indexes = {}
        self.correct_dates = []
        
        self._authenticate()
    
    def _authenticate(self):
        """Authenticate with Google Sheets API"""
        try:
            scope = [
                'https://spreadsheets.google.com/feeds',
                'https://www.googleapis.com/auth/drive'
            ]
            
            creds = Credentials.from_service_account_file(
                self.credentials_path, scopes=scope
            )
            
            self.client = gspread.authorize(creds)
            logger.info("Successfully authenticated with Google Sheets API")
            
        except Exception as e:
            logger.error(f"Failed to authenticate with Google Sheets: {e}")
            raise
    
    def open_spreadsheet(self, sheet_url: str):
        """Open the Google Spreadsheet"""
        try:
            self.spreadsheet = self.client.open_by_url(sheet_url)
            logger.info(f"Opened spreadsheet: {self.spreadsheet.title}")
        except Exception as e:
            logger.error(f"Failed to open spreadsheet: {e}")
            raise
    
    def load_correct_dates(self) -> List[str]:
        """Load dates from CORRECT DATES sheet"""
        try:
            correct_dates_sheet = self.spreadsheet.worksheet(self.correct_dates_sheet_name)
            
            # Get all values from column A
            dates_data = correct_dates_sheet.col_values(1)
            
            # Clean and format dates
            self.correct_dates = [str(date).strip() for date in dates_data if date]
            
            logger.info(f"Loaded {len(self.correct_dates)} dates from {self.correct_dates_sheet_name}")
            return self.correct_dates
            
        except gspread.WorksheetNotFound:
            raise Exception(f'Sheet "{self.correct_dates_sheet_name}" not found.')
        except Exception as e:
            logger.error(f"Failed to load correct dates: {e}")
            raise
    
    def load_data_sheets(self):
        """Load data from all required sheets"""
        try:
            for sheet_name in self.sheet_names:
                try:
                    sheet = self.spreadsheet.worksheet(sheet_name)
                    values = sheet.get_all_values()
                    
                    if not values:
                        logger.warning(f"Sheet {sheet_name} is empty")
                        continue
                    
                    # Store sheet data
                    self.data_sheets[sheet_name] = values
                    
                    # Create header index mapping
                    header_row = values[0]
                    header_map = {}
                    for i, header in enumerate(header_row):
                        if header:
                            header_map[str(header).strip()] = i
                    
                    self.header_indexes[sheet_name] = header_map
                    
                    logger.info(f"Loaded sheet {sheet_name} with {len(values)} rows")
                    
                except gspread.WorksheetNotFound:
                    raise Exception(f'Sheet "{sheet_name}" not found.')
            
            logger.info("All data sheets loaded successfully")
            
        except Exception as e:
            logger.error(f"Failed to load data sheets: {e}")
            raise
    
    def get_value(self, sheet_name: str, row_idx: int, date_key: str) -> Any:
        """Get value from a specific sheet, row, and date column"""
        try:
            data = self.data_sheets[sheet_name]
            headers = self.header_indexes[sheet_name]
            
            col_idx = headers.get(date_key)
            
            if (col_idx is not None and 
                row_idx < len(data) and 
                col_idx < len(data[row_idx]) and
                data[row_idx][col_idx] and 
                str(data[row_idx][col_idx]).strip()):
                
                return data[row_idx][col_idx]
            else:
                return 0
                
        except Exception as e:
            logger.warning(f"Error getting value for {sheet_name}, row {row_idx}, date {date_key}: {e}")
            return 0
    
    def format_date(self, raw_date: str) -> str:
        """Format date as MM/D/YY (equivalent to Apps Script formatDate function)"""
        try:
            # Try to parse the date
            if isinstance(raw_date, datetime):
                parsed_date = raw_date
            else:
                # Try different date formats
                date_formats = [
                    '%Y-%m-%d',
                    '%d/%m/%Y',
                    '%m/%d/%Y',
                    '%d-%m-%Y',
                    '%m-%d-%Y',
                    '%Y/%m/%d',
                    '%d.%m.%Y',
                    '%Y.%m.%d'
                ]
                
                parsed_date = None
                for fmt in date_formats:
                    try:
                        parsed_date = datetime.strptime(str(raw_date).strip(), fmt)
                        break
                    except ValueError:
                        continue
                
                if parsed_date is None:
                    # If parsing fails, return the original date
                    return str(raw_date)
              # Format as MM/D/YY
            month = parsed_date.month
            day = parsed_date.day
            year = str(parsed_date.year)[-2:]  # Last 2 digits of year
            
            return f"{month}/{day}/{year}"
            
        except Exception as e:
            logger.warning(f"Error formatting date {raw_date}: {e}")
            return str(raw_date)  # Fallback to original
    
    def create_or_get_output_sheet(self):
        """Create or get the output sheet"""
        try:
            # Try to get existing sheet
            try:
                output_sheet = self.spreadsheet.worksheet(self.output_sheet_name)
                logger.info(f"Found existing output sheet: {self.output_sheet_name}")
                return output_sheet
            except gspread.WorksheetNotFound:
                # Create new sheet
                output_sheet = self.spreadsheet.add_worksheet(
                    title=self.output_sheet_name,
                    rows=1000,
                    cols=10
                )
                
                # Add header row
                header_row = [
                    "#", "Website", "Type", "Date", 
                    "Traffic Average", "Traffic Monthly", "DR", "RD", "Keywords"
                ]
                output_sheet.append_row(header_row)
                
                logger.info(f"Created new output sheet: {self.output_sheet_name}")
                return output_sheet
                
        except Exception as e:
            logger.error(f"Failed to create/get output sheet: {e}")
            raise
    
    def generate_combined_report(self, sheet_url: str):
        """
        Main function to generate the combined report
        (Python equivalent of generateProperCombinedReport)
        """
        try:
            logger.info("Starting combined report generation")
            
            # Open spreadsheet
            self.open_spreadsheet(sheet_url)
            
            # Load data
            self.load_correct_dates()
            self.load_data_sheets()
            
            # Get main data sheet (Traffic Average) for row count
            if "Traffic Average" not in self.data_sheets:
                raise Exception("Traffic Average sheet is required")
            
            main_data = self.data_sheets["Traffic Average"]
            row_count = len(main_data)
            total_dates = len(self.correct_dates)
            
            logger.info(f"Processing {row_count} rows with {total_dates} dates")
            
            # Get or create output sheet
            output_sheet = self.create_or_get_output_sheet()
            
            records_written = 0
            
            # Process all data in one go
            for i in range(1, row_count):  # Start from row 1 (skip header)
                for j in range(total_dates):
                    # Get data from Traffic Average sheet (main sheet)
                    if i >= len(main_data) or len(main_data[i]) < 3:
                        logger.warning(f"Insufficient data in row {i}")
                        continue
                    
                    number = main_data[i][0] if len(main_data[i]) > 0 else ""
                    website = main_data[i][1] if len(main_data[i]) > 1 else ""
                    type_value = main_data[i][2] if len(main_data[i]) > 2 else ""
                    
                    raw_date = self.correct_dates[j]
                    formatted_date = self.format_date(raw_date)
                    
                    # Get values from all sheets for this row and date
                    row_data = [
                        number,
                        website,
                        type_value,
                        formatted_date,
                        self.get_value("Traffic Average", i, raw_date),
                        self.get_value("Traffic Monthly", i, raw_date),
                        self.get_value("DR", i, raw_date),
                        self.get_value("RD", i, raw_date),
                        self.get_value("Keywords", i, raw_date)
                    ]
                      # Append row to output sheet
                    output_sheet.append_row(row_data)
                    records_written += 1
            
            logger.info("✅ All data processed successfully!")
            logger.info(f"Total records written: {records_written}")
            return True
            
        except Exception as e:
            logger.error(f"Error generating combined report: {e}")
            raise


def main():
    """Main execution function"""
    try:
        # Configuration
        credentials_path = GOOGLE_SHEET_CONFIG['credentials_path']
        sheet_url = GOOGLE_SHEET_CONFIG['sheet_url']
        
        logger.info("Starting Combined Report Generator")
        
        # Initialize generator
        generator = CombinedReportGenerator(credentials_path)
        
        # Generate report
        logger.info("Processing all data and generating combined report...")
        generator.generate_combined_report(sheet_url)
        
        logger.info("Report generation completed!")
            
    except Exception as e:
        logger.error(f"Main execution failed: {e}")
        raise


if __name__ == "__main__":
    main()
