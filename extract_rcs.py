# not entirely sure what this was for, ignore i guess

import csv

def extract_unique_values(input_csv, output_file):
    try:
        unique_values = set()
        
        # Read the input CSV file
        with open(input_csv, 'r', newline='', encoding='utf-8') as csvfile:
            reader = csv.DictReader(csvfile)
            if 'B' not in reader.fieldnames:
                print("Column 'B' not found in the CSV file.")
                return
            
            # Collect unique values from Column B, converting to lowercase and stripping whitespace
            for row in reader:
                value = row['B'].strip().lower()  # Normalize the value
                unique_values.add(value)
        
        # Write unique values to the output file
        with open(output_file, 'w', encoding='utf-8') as outfile:
            for value in sorted(unique_values):  # Sorting is optional
                outfile.write(value + '\n')
        
        print(f"Unique values from Column B have been saved to {output_file}.")
    except Exception as e:
        print(f"An error occurred: {e}")

# Example usage
input_csv = 'response.csv'  # Replace with your input CSV file path
output_file = 'unique_values.txt'  # Replace with your desired output file path
extract_unique_values(input_csv, output_file)
