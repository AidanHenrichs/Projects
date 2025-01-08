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

# Function to convert date to unix
def date_to_unix(date_str, date_format="%Y-%m-%d %H:%M:%S"):
    dt = datetime.strptime(date_str, date_format)
    return dt.timestamp()

# Function to analyze using VADER
def analyze_sentiment_vader(comment):
    sentiment = sia.polarity_scores(comment)
    compound_score = sentiment['compound']
    return compound_score

try:
    sia = SentimentIntensityAnalyzer()
except:
    nltk.download('vader_lexicon')
    sia = SentimentIntensityAnalyzer()

# Load Data
reddit_data = pd.read_csv('C:/Users/ash/PycharmProjects/636-dataproject/data/combined_reddit.csv')  # Scraped Reddit posts
stock_data = pd.read_csv('C:/Users/ash/PycharmProjects/636-dataproject/data/combined_prices.csv')  # Historical stock data
news_data = pd.read_csv('C:/Users/ash/PycharmProjects/636-dataproject/data/combine_news.csv')  # News headlines

# Preprocessing
# Reddit Sentiment scored with vader
reddit_data['sentiment'] = reddit_data['comment'].apply(lambda x: analyze_sentiment_vader(x))
reddit_data['WeightedSentiment'] = reddit_data['sentiment'] * reddit_data['score']

company_sentiment = reddit_data.groupby('company').agg(
    WeightedSentimentSum=('WeightedSentiment', 'sum'),
    ScoreSum=('score', 'sum')
).reset_index()
company_sentiment['WeightedSentiment'] = company_sentiment.apply(
    lambda row: row['WeightedSentimentSum'] / row['ScoreSum'] if row['ScoreSum'] != 0 else 0, axis=1)

#news sentiment scored with vader
news_data['sentiment'] = news_data['Summary'].apply(lambda x: analyze_sentiment_vader(x))

#rename column form merge
news_data = news_data.rename(columns={'Company': 'company'})

#clean company name for merge
news_data['company'] = news_data['company'].str.replace('news_','')

# Get weighted avg by company
news_sentiment = news_data.groupby('company').agg(WeightedSentimentMean=('sentiment', 'mean')).reset_index()

# Merge sentiment data
company_sentiment = company_sentiment[['company', 'WeightedSentiment']]
news_sentiment = news_sentiment[['company', 'WeightedSentimentMean']]

sentiment_data = pd.merge(company_sentiment, news_sentiment, on='company', how='inner')
sentiment_data = sentiment_data.sort_values(by='company')

#process stock_data
stock_data['Volume'] = stock_data['Volume'].apply(lambda x: float(x.replace(",", "")))
stock_data.fillna(0, inplace=True)

#clean data
stock_data['company'] = stock_data['Company'].str.replace('price_', '')
stock_data =stock_data.sort_values(by='company')

# Merge preprocessed stock_data with temp_data
merged_data = stock_data.merge(sentiment_data, on='company')
merged_data[['Open', 'Close', 'Volume', 'WeightedSentiment', 'WeightedSentimentMean']] = merged_data[
    ['Open', 'Close', 'Volume', 'WeightedSentiment', 'WeightedSentimentMean']
].fillna(0)

# Stock Data Features
scaler = StandardScaler()
merged_data[['Open', 'Close', 'Volume']] = scaler.fit_transform(stock_data[['Open', 'Close', 'Volume']])

# Create labels (binary classification: 'Increase' or 'Decrease')
merged_data['Label'] = np.where(merged_data['Close'] > merged_data['Open'], 'Increase', 'Decrease')
features = merged_data[['Open', 'Close', 'Volume', 'WeightedSentiment', 'WeightedSentimentMean']].fillna(0)
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
