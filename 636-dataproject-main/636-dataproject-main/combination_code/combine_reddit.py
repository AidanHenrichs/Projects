import os
import pandas as pd

# Path to the data folder
data_folder = "/home/z1988135/636-dataproject/data"

# List all files in the data folder
files = [f for f in os.listdir(data_folder) if f.endswith(".csv")]

# Exclude financials.csv explicitly
excluded_files = ["financials.csv", "filtered_comments_with_features.csv", "combined_dataset.csv"]
files_to_combine = [f for f in files if f not in excluded_files]

# Combine all company CSV files
dataframes = []

for file in files_to_combine:
    file_path = os.path.join(data_folder, file)
    df = pd.read_csv(file_path)
    df['company'] = file.split('.')[0]  # Add a column to identify the company
    dataframes.append(df)

# Combine all dataframes
combined_df = pd.concat(dataframes, ignore_index=True)

# Save the combined dataframe to the data folder
combined_file_path = os.path.join(data_folder, "combined_dataset.csv")
combined_df.to_csv(combined_file_path, index=False)

print(f"Combined dataset saved to {combined_file_path}")
