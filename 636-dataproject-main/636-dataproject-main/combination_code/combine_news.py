import os
import csv
import re

# Define input folder and output file paths
input_folder = "/workspaces/636-dataproject/data/backupdata/news"
output_file = "/workspaces/636-dataproject/data/combine_news.csv"

# Function to process a single file
def process_file(file_path, company_name):
    articles = []
    skipped_entries = []  # Track skipped entries for debugging

    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
        # Split entries based on bullet points or quoted titles
        entries = content.split("•\n") if "•" in content else re.split(r'(?<=\n)"', content.strip())

        for entry in entries:
            lines = entry.strip().split("\n")
            if len(lines) > 1:
                title = None
                summary_lines = []
                stock_change = None
                published = "Unknown"
                source = "Unknown"

                for i, line in enumerate(lines):
                    line = line.strip()

                    # Handle Walmart-specific case where source is in the title
                    if company_name == "news_wmt" and "–" in line and title is None:
                        parts = line.split(" – ", 1)
                        title = parts[0].strip()
                        source = parts[1].strip() if len(parts) > 1 else "Unknown"
                        continue

                    # Identify title as the first meaningful line
                    if title is None and len(line) > 10 and not re.search(r"(days ago|[-+]\d+\.\d+%)", line) and "Source:" not in line:
                        title = line
                        continue

                    # Identify published dates and move them out of the summary
                    if "Published:" in line:
                        published = line.split("Published:")[1].strip()
                        continue
                    elif re.search(r"days ago", line) and published == "Unknown":
                        published = "Unknown"  # For Powell or others with "days ago"
                        continue

                    # Identify stock changes
                    if re.search(r"[-+]\d+\.\d+%", line):
                        stock_change = line
                        continue

                    # Extract source
                    if "Source:" in line:
                        source = line.split("Source:")[1].strip()
                        continue

                    # Add remaining lines to the summary (ignore title line)
                    if i > 0:  # Ensure the first line (title) is not added to the summary
                        summary_lines.append(line)

                # Combine summary lines into one string
                summary = " ".join(summary_lines).strip()

                # Remove title if it inadvertently appears in the summary
                if title in summary:
                    summary = summary.replace(title, "").strip()

                # Append stock change to the summary if available
                if stock_change:
                    summary += f" Stock Change: {stock_change}"

                # Append the article to the list if valid
                if title:
                    articles.append([company_name, title, published, source, summary])
                else:
                    skipped_entries.append(entry)
            else:
                skipped_entries.append(entry)

    # Debugging for skipped entries
    if skipped_entries:
        print(f"{len(skipped_entries)} entries skipped in {file_path}: {skipped_entries}")

    return articles

# Process all .txt files in the input folder
all_articles = []

for filename in os.listdir(input_folder):
    if filename.endswith(".txt"):
        company_name = filename.replace(".txt", "")
        file_path = os.path.join(input_folder, filename)
        print(f"Processing {file_path}")
        articles = process_file(file_path, company_name)
        print(f"Extracted {len(articles)} articles from {file_path}")
        all_articles.extend(articles)

# Write processed data to CSV
output_headers = ["Company", "Title", "Published", "Source", "Summary"]

with open(output_file, 'w', newline='', encoding='utf-8') as csvfile:
    writer = csv.writer(csvfile)
    writer.writerow(output_headers)  # Write header
    writer.writerows(all_articles)  # Write rows

print(f"Data successfully saved to {output_file}.")
