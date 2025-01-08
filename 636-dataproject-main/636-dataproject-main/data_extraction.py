import pandas as pd
import praw
import time
import requests
from bs4 import BeautifulSoup
import re

# Reddit API credentials
client_id = '0g9lCAnzXBGm_NfCtRG1Eg'
client_secret = '_HyRrtKJxfT6MhOocqC_L6s9mhNjKQ'
user_agent = 'my_reddit_scraper/0.1 by u/benjamin'

# Initialize the PRAW client
reddit = praw.Reddit(client_id=client_id, client_secret=client_secret, user_agent=user_agent)

# Function to get comments containing a specific keyword
def get_comments_with_keyword(thread_url, keyword):
    # Load the Reddit submission (thread) by URL
    submission = reddit.submission(url=thread_url)

    # Replace "replace_more" to expand all comments
    submission.comments.replace_more(limit=None)

    # List to store comments that contain the keyword
    matching_comments = []

    # Search through each comment for the keyword
    for comment in submission.comments.list():
        if keyword.lower() in comment.body.lower():                                 # case-insensitive search
            # logging for runtime
            matching_comments.append({
                #'author': comment.author.name if comment.author else '[deleted]',  # author
                'comment': comment.body,
                'score': comment.score,                                             # upvotes
                'created_utc': comment.created_utc                                  # time created
            })

    return matching_comments

# Function to get company financials from ALPH query for ticker in question
def fetch_company_metrics(url):
     # Make a request to the webpage
    response = requests.get(url)

    # Check if the request was successful
    if response.status_code == 200:
        print(f"Successfully fetched the page for {url}.")
        # Parse the HTML content
        soup = BeautifulSoup(response.text, 'html.parser')

        # Debugging
        # print(soup.prettify())

        return soup.prettify()
    else:
        print(f"Failed to retrieve the webpage for {url}. Status code: {response.status_code}")
        return None

# Function to save comments to CSV
def save_comments_to_csv(comments, filename="filtered_comments.csv"):
    # Convert the list of dictionaries to a DataFrame
    df = pd.DataFrame(comments)

    # Save DataFrame to CSV
    df.to_csv(filename, index=False)
    print(f"Comments saved to {filename}")

# Example usage
if __name__ == "__main__":
    startTime = time.time()

    thread_url = "https://www.reddit.com/r/wallstreetbets/comments/1grybzd/weekly_earnings_thread_1118_1122/"  # Replace with your desired thread URL
    keyword = "POWL"  # Keyword to search for in comments

    comments = get_comments_with_keyword(thread_url, keyword)

    # debugging: logging comments to console after request and collection completed
    '''
    for idx, comment in enumerate(comments, 1):
        print(f"{idx}. Author: {comment['author']}\nScore: {comment['score']}\nComment: {comment['comment']}\n")
    for metric, value in metrics.items():
        print(f"{metric}: {value}")
    '''

    # finalize: save comments to .csv file for manipulation
    save_comments_to_csv(comments, filename="data/powl.csv")

    endTime = time.time()

    print("Collection Completed in ", endTime - startTime, "seconds!")

print("Program Executed!")

# 275.729 seconds (last run)
