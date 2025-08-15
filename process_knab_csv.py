#!/usr/bin/env python3
"""
Knab CSV Transaction Processor

This script processes Knab bank transaction CSV exports and extracts only the essential fields:
- Transactiedatum (Transaction Date)
- Bedrag (Amount) 
- Omschrijving (Description)

Input: Knab bank export CSV file with semicolon delimiters
Output: Clean CSV with only the 3 required fields
"""

import csv
import os
import sys
from datetime import datetime
import re

def process_knab_csv(input_file_path, output_file_path=None):
    """
    Process Knab CSV file and extract only Transactiedatum, Bedrag, and Omschrijving fields.
    
    Args:
        input_file_path (str): Path to the input Knab CSV file
        output_file_path (str): Path for the output CSV file (optional)
    
    Returns:
        str: Path to the processed CSV file
    """
    
    # Generate output filename if not provided
    if output_file_path is None:
        base_name = os.path.splitext(os.path.basename(input_file_path))[0]
        output_file_path = f"{base_name}_processed.csv"
    
    # Track statistics
    total_rows = 0
    processed_rows = 0
    skipped_rows = 0
    
    try:
        with open(input_file_path, 'r', encoding='utf-8') as infile:
            # Read the file content
            content = infile.read()
            
        # Split into lines
        lines = content.strip().split('\n')
        
        # Find the header line (should contain "Rekeningnummer;Transactiedatum;...")
        header_line_index = -1
        for i, line in enumerate(lines):
            if 'Rekeningnummer' in line and 'Transactiedatum' in line and 'Omschrijving' in line:
                header_line_index = i
                break
        
        if header_line_index == -1:
            raise ValueError("Could not find header line in CSV file")
        
        # Parse header to find column positions
        header_line = lines[header_line_index]
        headers = [h.strip('"') for h in header_line.split(';')]
        
        # Find the indices of our target columns
        try:
            transactiedatum_idx = headers.index('Transactiedatum')
            bedrag_idx = headers.index('Bedrag')
            omschrijving_idx = headers.index('Omschrijving')
        except ValueError as e:
            raise ValueError(f"Required column not found in headers: {e}")
        
        print(f"Found columns at positions:")
        print(f"  Transactiedatum: {transactiedatum_idx}")
        print(f"  Bedrag: {bedrag_idx}")
        print(f"  Omschrijving: {omschrijving_idx}")
        
        # Process data lines
        processed_data = []
        
        # Start from the line after the header
        for line_num, line in enumerate(lines[header_line_index + 1:], start=header_line_index + 2):
            total_rows += 1
            
            # Skip empty lines
            if not line.strip():
                skipped_rows += 1
                continue
            
            # Parse the line using CSV reader for proper quote handling
            try:
                # Use StringIO to simulate a file for csv.reader
                from io import StringIO
                csv_reader = csv.reader(StringIO(line), delimiter=';')
                row = next(csv_reader)
                
                # Check if we have enough columns
                if len(row) <= max(transactiedatum_idx, bedrag_idx, omschrijving_idx):
                    print(f"Warning: Line {line_num} has insufficient columns, skipping")
                    skipped_rows += 1
                    continue
                
                # Extract the target fields
                transactiedatum = row[transactiedatum_idx].strip('"').strip()
                bedrag = row[bedrag_idx].strip('"').strip()
                omschrijving = row[omschrijving_idx].strip('"').strip()
                
                # Validate date format (DD-MM-YYYY)
                if not re.match(r'\d{2}-\d{2}-\d{4}', transactiedatum):
                    print(f"Warning: Line {line_num} has invalid date format '{transactiedatum}', skipping")
                    skipped_rows += 1
                    continue
                
                # Validate amount (should be numeric, possibly with comma as decimal separator)
                if not re.match(r'^\d+([,\.]\d+)?$', bedrag):
                    print(f"Warning: Line {line_num} has invalid amount format '{bedrag}', skipping")
                    skipped_rows += 1
                    continue
                
                # Add to processed data
                processed_data.append([transactiedatum, bedrag, omschrijving])
                processed_rows += 1
                
            except Exception as e:
                print(f"Error processing line {line_num}: {e}")
                skipped_rows += 1
                continue
        
        # Write the processed data to output file
        with open(output_file_path, 'w', newline='', encoding='utf-8') as outfile:
            writer = csv.writer(outfile, delimiter=';')
            
            # Write header
            writer.writerow(['Transactiedatum', 'Bedrag', 'Omschrijving'])
            
            # Write data
            for row in processed_data:
                writer.writerow(row)
        
        # Print statistics
        print(f"\n✅ Processing completed successfully!")
        print(f"📊 Statistics:")
        print(f"  Total rows found: {total_rows}")
        print(f"  Successfully processed: {processed_rows}")
        print(f"  Skipped/invalid: {skipped_rows}")
        print(f"  Output file: {output_file_path}")
        
        return output_file_path
        
    except FileNotFoundError:
        print(f"❌ Error: Input file '{input_file_path}' not found")
        return None
    except Exception as e:
        print(f"❌ Error processing file: {e}")
        return None

def main():
    """Main function for command line usage"""
    
    if len(sys.argv) < 2:
        print("Usage: python process_knab_csv.py <input_csv_file> [output_csv_file]")
        print("\nExample:")
        print("  python process_knab_csv.py 'Knab Transactieoverzicht.csv'")
        print("  python process_knab_csv.py 'input.csv' 'output.csv'")
        sys.exit(1)
    
    input_file = sys.argv[1]
    output_file = sys.argv[2] if len(sys.argv) > 2 else None
    
    print(f"🔄 Processing Knab CSV file: {input_file}")
    
    result = process_knab_csv(input_file, output_file)
    
    if result:
        print(f"✅ File processed successfully: {result}")
    else:
        print("❌ Failed to process file")
        sys.exit(1)

if __name__ == "__main__":
    main()
