from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from bs4 import BeautifulSoup
import csv
import time
from datetime import datetime, timedelta

# Keywords to filter headlines
keywords = ["Nvidia", "NVDA"]

# Path to your ChromeDriver
CHROMEDRIVER_PATH = r'C:\Users\corey\OneDrive\Desktop\chromedriver-win64\chromedriver.exe'

# Custom time range (in days)
min_days_ago = 5  # Earliest time ago (e.g., 5 days ago)
max_days_ago = 10  # Latest time ago (e.g., 10 days ago)

# Calculate the date range
end_time = datetime.now() - timedelta(days=min_days_ago)
start_time = datetime.now() - timedelta(days=max_days_ago)

# Set up the Selenium WebDriver with headless mode for efficiency
service = Service(CHROMEDRIVER_PATH)
options = webdriver.ChromeOptions()
options.add_argument('--headless')
driver = webdriver.Chrome(service=service, options=options)

def parse_relative_time(relative_time):
    """Convert relative time (e.g., '5 hours ago', 'yesterday', 'last month') to a datetime object."""
    now = datetime.now()
    try:
        if "hour" in relative_time:
            hours = int(relative_time.split()[0])
            return now - timedelta(hours=hours)
        elif "day" in relative_time:
            days = int(relative_time.split()[0])
            return now - timedelta(days=days)
        elif "minute" in relative_time:
            minutes = int(relative_time.split()[0])
            return now - timedelta(minutes=minutes)
        elif "yesterday" in relative_time.lower():
            return now - timedelta(days=1)
        elif "month" in relative_time.lower():
            # Assume "last month" is 30 days ago for simplicity
            return now - timedelta(days=30)
        elif "week" in relative_time.lower():
            weeks = int(relative_time.split()[0])
            return now - timedelta(weeks=weeks)
        elif "just now" in relative_time.lower() or "moments" in relative_time.lower():
            return now  # Consider "Just now" as the current time
        else:
            print(f"Unrecognized relative time format: {relative_time}")  # Debugging output
            return None  # Return None for unrecognized formats
    except (ValueError, IndexError):
        print(f"Error parsing relative time: {relative_time}")  # Debugging output
        return None  # Return None if parsing fails

try:
    # Navigate to Yahoo Finance News page
    url = 'https://finance.yahoo.com/quote/NVDA/news/'
    driver.get(url)

    # Scroll to load more content
    for _ in range(50):  # Adjust scroll count as needed
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        time.sleep(3)  # Wait for content to load

    # Get the loaded page source
    soup = BeautifulSoup(driver.page_source, 'html.parser')

    # Generate a CSV file name dynamically based on the keywords
    csv_filename = f"{'_'.join(keywords)}_Headlines.csv"

    # Find all headline elements
    articles = soup.find_all('li', class_='stream-item story-item yf-1usaaz9')
    print(f"Total headlines found after scrolling: {len(articles)}")  # Debugging: Check total count

    # Open a CSV file to save filtered headlines and dates
    with open(csv_filename, 'w', newline='', encoding='utf-8') as file:
        writer = csv.writer(file)
        writer.writerow(['Headline', 'Date'])  # Write header

        # Extract and write each headline and date
        for article in articles:
            headline_tag = article.find('h3', class_='clamp')  # Adjust selector as needed
            date_tag = article.find('div', class_='publishing yf-1weyqlp')
            if date_tag:
                raw_text = date_tag.get_text().strip()  # Full text: "Insider Monkey • 5 days ago"
                date_text = raw_text.split('•')[-1].strip() if '•' in raw_text else 'N/A'
                article_date = parse_relative_time(date_text)
            else:
                article_date = None

            if headline_tag and article_date:
                title = headline_tag.get_text().strip()

                # Filter by keyword and publish date within the range
                if (any(keyword.lower() in title.lower() for keyword in keywords) and
                        start_time <= article_date <= end_time):
                    writer.writerow([title, article_date.strftime('%Y-%m-%d %H:%M:%S')])
                    print("Matching article:", title, "| Date:", article_date)  # Debugging output

    print(f"Filtered headlines have been saved to '{csv_filename}'")
finally:
    driver.quit()
