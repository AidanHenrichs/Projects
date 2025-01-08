import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import classification_report
from nltk.sentiment import SentimentIntensityAnalyzer
from datetime import datetime
from nltk.classify import NaiveBayesClassifier
from nltk.corpus import subjectivity
from nltk.sentiment import SentimentAnalyzer
from nltk.sentiment.util import *
import pandas as pd
import torch
from transformers import AutoTokenizer, AutoModelForSequenceClassification
from torch.nn.functional import softmax
#
#
# Data needs to be merged in a way where we can get sentiment from reddit and news, and match it with stock
# The length difference wont allow us to use train_split accurately
#
#


# Function to convert date to unix
def date_to_unix(date_str, date_format="%Y-%m-%d %H:%M:%S"):
    dt = datetime.strptime(date_str, date_format)
    return dt.timestamp()

# Function for sentiment analysis using Twitter-RoBERTa
def analyze_sentiment_bert(model_name, comments):
    tokenizer = AutoTokenizer.from_pretrained(model_name)
    model = AutoModelForSequenceClassification.from_pretrained(model_name)

    sentiments = []
    for comment in comments:
        inputs = tokenizer(comment, return_tensors="pt", truncation=True, padding=True, max_length=512)
        outputs = model(**inputs)
        probabilities = softmax(outputs.logits, dim=-1).detach().numpy()[0]
        sentiment_score = probabilities[2] - probabilities[0]  # Positive - Negative
        sentiments.append(sentiment_score)
    return sentiments

# Load Twitter-RoBERTa model and tokenizer
model_name = "cardiffnlp/twitter-roberta-base-sentiment"
tokenizer = AutoTokenizer.from_pretrained(model_name)
model = AutoModelForSequenceClassification.from_pretrained(model_name)

# 1. Load Data
reddit_data = pd.read_csv('C:/Users/ash/PycharmProjects/636-dataproject/data/combined_reddit.csv')  # Scraped Reddit posts
stock_data = pd.read_csv('C:/Users/ash/PycharmProjects/636-dataproject/data/combined_prices.csv')  # Historical stock data
news_data = pd.read_csv('C:/Users/ash/PycharmProjects/636-dataproject/data/combine_news.csv')  # News headlines

# Sentiment Analysis for Reddit Data (Using RoBERTa)
print("Analyzing Reddit data sentiment using RoBERTa...")
reddit_model_name = "cardiffnlp/twitter-roberta-base-sentiment"
reddit_data['SentimentScore'] = analyze_sentiment_bert(reddit_model_name, reddit_data['comment'])

# Sentiment Analysis for News Data (Using FinBERT)
print("Analyzing News data sentiment using FinBERT...")
news_model_name = "yiyanghkust/finbert-tone"
news_data['SentimentScore'] = analyze_sentiment_bert(news_model_name, news_data['Summary'])

# Combine weighted sentiment scores
reddit_data['WeightedSentiment'] = reddit_data['SentimentScore'] * reddit_data['score']
news_data['WeightedSentiment'] = news_data['SentimentScore']

# Aggregating Reddit sentiment by company
reddit_sentiment = reddit_data.groupby('company').agg(
    WeightedSentimentSum=('WeightedSentiment', 'sum'),
    ScoreSum=('score', 'sum')
).reset_index()

reddit_sentiment['WeightedSentiment'] = reddit_sentiment.apply(
    lambda row: row['WeightedSentimentSum'] / row['ScoreSum'] if row['ScoreSum'] != 0 else 0,
    axis=1
)

# Aggregating News sentiment by company
news_sentiment = news_data.groupby('Company').agg(
    SentimentAvg=('SentimentScore', 'mean')
).reset_index()

# Merging aggregated sentiment with stock data
print("Combining sentiment data with stock performance data...")
merged_data = stock_data.merge(reddit_sentiment[['company', 'WeightedSentiment']], left_on='Company', right_on='company', how='left')
merged_data = merged_data.merge(news_sentiment, on='Company', how='left')
# Preprocessing: Handle numeric conversions and missing values in stock data
def clean_numeric_column(column):
    """Converts a column to numeric by removing commas and handling NaN values."""
    return column.apply(lambda x: float(str(x).replace(",", "")) if pd.notnull(x) else 0)

stock_data['Volume'] = clean_numeric_column(stock_data['Volume'])
stock_data['Open'] = clean_numeric_column(stock_data['Open'])
stock_data['Close'] = clean_numeric_column(stock_data['Close'])

# Merge sentiment data with stock data
merged_data = stock_data.merge(reddit_sentiment[['company', 'WeightedSentiment']], left_on='Company', right_on='company', how='left')
merged_data = merged_data.merge(news_sentiment, on='Company', how='left')

# Handle any remaining NaN values
merged_data[['Open', 'Close', 'Volume', 'WeightedSentiment', 'SentimentAvg']] = merged_data[
    ['Open', 'Close', 'Volume', 'WeightedSentiment', 'SentimentAvg']
].fillna(0)

# Feature Scaling: Standardize stock data features
scaler = StandardScaler()
merged_data[['Open', 'Close', 'Volume']] = scaler.fit_transform(merged_data[['Open', 'Close', 'Volume']])

# Feature Engineering
scaler = StandardScaler()
merged_data[['Open', 'Close', 'Volume']] = scaler.fit_transform(merged_data[['Open', 'Close', 'Volume']])

# Create labels (binary classification: 'Increase' or 'Decrease')
merged_data['Label'] = np.where(merged_data['Close'] > merged_data['Open'], 'Increase', 'Decrease')

# Prepare data for model training
features = merged_data[['Open', 'Close', 'Volume', 'WeightedSentiment', 'SentimentAvg']].fillna(0)
labels = merged_data['Label']

# Train/Test Split
X_train, X_test, y_train, y_test = train_test_split(
    features, labels, test_size=0.3, random_state=42)


# Prepare data for NaiveBayesClassifier
train_data = [({f'feature_{i}': X_train.iloc[j, i] for i in range(len(X_train.columns))}, y_train.iloc[j]) for j in range(len(X_train))]
test_data = [({f'feature_{i}': X_test.iloc[j, i] for i in range(len(X_test.columns))}, y_test.iloc[j]) for j in range(len(X_test))]
# Train the NaiveBayesClassifier
classifier = NaiveBayesClassifier.train(train_data)

# Evaluation
accuracy = nltk.classify.accuracy(classifier, test_data)
print(f"Accuracy: {accuracy}")

y_pred = [classifier.classify({f'feature_{i}': X_test.iloc[j, i] for i in range(len(X_test.columns))}) for j in range(len(X_test))]
print(classification_report(y_test, y_pred))
