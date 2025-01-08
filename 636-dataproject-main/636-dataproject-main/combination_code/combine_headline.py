import os
import pandas as pd

# Define input folder and output file
input_folder = '/workspaces/636-dataproject/Yahoo Finance Headlines'  # Replace with the folder containing your 10 company files
output_file = '/workspaces/636-dataproject/data/combined_headline.csv'  # Replace with the desired output file path

# Initialize an empty DataFrame to store combined data
combined_data = pd.DataFrame()

# Loop through each file in the input folder
for file_name in os.listdir(input_folder):
    if file_name.endswith('.csv'):  # Only process CSV files
        # Extract the company name from the file name (assuming the file name contains the company name)
        company_name = file_name.split('.')[0]  # Removes the .csv extension
        
        # Load the company's data
        file_path = os.path.join(input_folder, file_name)
        company_data = pd.read_csv(file_path)
        
        # Add a new column for the company name
        company_data['Company'] = company_name
        
        # Append the company's data to the combined DataFrame
        combined_data = pd.concat([combined_data, company_data], ignore_index=True)

# Fill missing values in the combined dataset with "Unknown"
combined_data.fillna("Unknown", inplace=True)

# Save the combined data to a single CSV file
combined_data.to_csv(output_file, index=False)

print(f"Combined data saved to {output_file} with missing values filled as 'Unknown'")
