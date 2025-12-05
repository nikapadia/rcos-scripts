import pandas as pd
import glob
import os
import re
from dateutil import parser

# CONFIGURATION
INPUT_DIRECTORY = './csv_files'  # Folder where your CSVs are located
OUTPUT_FILENAME = 'workshops_gradebook.csv'

def parse_filename_info(filename):
    """
    Parses the filename to extract the Title and the Date object.
    Format expected: "RCOS [TITLE] - [DATE STRING] Attendance.csv"
    """
    base_name = os.path.basename(filename).replace('.csv', '')
    
    # We split by ' - ' starting from the RIGHT (maxsplit=1).
    # This ensures that if the Title contains a hyphen, it isn't broken up.
    # parts[0] = Title part
    # parts[1] = Date part
    try:
        parts = base_name.rsplit(' - ', 1)
        
        if len(parts) < 2:
            return None, base_name # Fallback if format doesn't match
            
        title_raw = parts[0].strip()
        title_raw = re.sub(r'^RCOS\s*', '', title_raw).strip()
        title_raw = title_raw.replace(',', '_')
        date_str = parts[1].replace(' Attendance', '').strip()
        
        # Normalize common quirks so dateutil can parse reliably:
        # - replace underscores in times like "5_50" => "5:50"
        # - normalize a.m./p.m. variants to AM/PM
        # - remove stray characters like '@' and compress whitespace
        date_str = re.sub(r'(\d+)[_](\d+)', r'\1:\2', date_str)      # 5_50 -> 5:50
        date_str = date_str.replace('p.m.', 'PM').replace('a.m.', 'AM')
        date_str = date_str.replace('p.m', 'PM').replace('a.m', 'AM')
        date_str = date_str.replace('@', ' ')
        date_str = re.sub(r'\s+', ' ', date_str).strip()

        # Try parsing
        try:
            date_obj = parser.parse(date_str, fuzzy=True)
            return date_obj, title_raw
        except Exception:
            # Second attempt with looser cleanup (remove weekday name if present)
            try:
                # Remove leading weekday tokens like "Mon", "Tue", etc.
                date_no_weekday = re.sub(r'^[A-Za-z]{3,}\s+', '', date_str)
                date_obj = parser.parse(date_no_weekday, fuzzy=True)
                return date_obj, title_raw
            except Exception as e:
                print(f"Warning: Could not parse date from '{filename}'. Error: {e}")
                return None, base_name
        
    except Exception as e:
        print(f"Warning: Could not parse date from '{filename}'. Error: {e}")
        return None, base_name

def main():
    # 1. Get list of all CSV files
    csv_files = glob.glob(os.path.join(INPUT_DIRECTORY, "*.csv"))
    
    if not csv_files:
        print("No CSV files found in the directory.")
        return

    # 2. Parse filenames and Sort them by Date
    # We create a list of dictionaries: [{'file': path, 'date': datetime, 'title': string}]
    file_metadata = []
    
    for f in csv_files:
        dt, title = parse_filename_info(f)
        if dt:
            file_metadata.append({'path': f, 'date': dt, 'title': title})
        else:
            # If date parsing fails, put it at the end
            file_metadata.append({'path': f, 'date': pd.Timestamp.max, 'title': title})

    # Sort the list by the date object
    file_metadata.sort(key=lambda x: x['date'])

    print(f"Found {len(file_metadata)} files. Processing in chronological order...")

    # 3. Process the files
    # We will start with an empty DataFrame and merge each file into it
    master_df = pd.DataFrame()
    
    # We need to keep track of the specific title column names to calculate total later
    grade_columns = []
    num_processed = 0
    num_failed = 0
    for item in file_metadata:
        file_path = item['path']
        col_title = item['title']
        print(f"Processing: {col_title} ({item['date']})")

        # Read CSV
        # We assume standard format: user id, given name, family name, grade1, totalgrade
        # We only need the first 4 columns.
        try:
            df = pd.read_csv(file_path)
            
            # Normalize column names to lowercase to be safe, then rename for clarity
            df.columns = [c.strip().lower() for c in df.columns]
            
            # Mapping based on your provided format:
            # user id (0), given name (1), family name (2), grade1 (3)
            # We rename 'grade1' to the 'col_title'
            df = df.iloc[:, 0:4] # Keep first 4 cols
            df.columns = ['user_id', 'given_name', 'family_name', col_title]
            
            # Force grade to be numeric, coerce errors (text) to NaN then 0
            df[col_title] = pd.to_numeric(df[col_title], errors='coerce').fillna(0)
            
            grade_columns.append(col_title)

            # MERGE LOGIC
            if master_df.empty:
                master_df = df
            else:
                # Outer merge ensures we keep students even if they are only in one file
                master_df = pd.merge(master_df, df, on=['user_id', 'given_name', 'family_name'], how='outer')
            num_processed += 1

        except Exception as e:
            num_failed += 1
            print(f"Error processing file {file_path}: {e}")

    # 4. Final Cleanup
    
    # Fill NaN (students who didn't exist in a specific CSV) with 0
    master_df[grade_columns] = master_df[grade_columns].fillna(0)

    # Calculate Total Grade
    master_df['Total Grade'] = master_df[grade_columns].sum(axis=1)

    # 5. Save to CSV
    # Ensure columns are in the nice order: ID, Name, Last, Title1, Title2..., Total
    cols = ['user_id', 'given_name', 'family_name'] + grade_columns + ['Total Grade']
    master_df = master_df[cols]
    
    master_df.to_csv(OUTPUT_FILENAME, index=False)
    print(f"\nSuccess! Combined grades saved to: {OUTPUT_FILENAME}")
    print(f"Total files successfully processed: {num_processed} ({num_processed/len(file_metadata)*100:.2f}%)")
    print(f"Total files failed to process: {num_failed}")

if __name__ == "__main__":
    main()