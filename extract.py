import pandas as pd
import json
import os

# Load the CSV file into a DataFrame
csv_file_path = "RecordList20241006.csv"  # Replace with your CSV file path
df = pd.read_csv(csv_file_path)

# Create a directory to save JSON files if it doesn't exist
output_dir = "output_simple"
os.makedirs(output_dir, exist_ok=True)

# Iterate over each row in the DataFrame
for index, row in df.iterrows():
    # Convert the row to a dictionary
    row_dict = row.to_dict()

    # Create a JSON file for each row
    json_file_path = os.path.join(
        output_dir, f"{row_dict["permit_number"]}.json"
    )  # JSON file named row_1.json, row_2.json, etc.

    # Write the dictionary to a JSON file
    with open(json_file_path, "w") as json_file:
        json.dump(row_dict, json_file, indent=4)

    print(f"Saved: {json_file_path}")
