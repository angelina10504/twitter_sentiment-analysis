# data_loader.py

import pandas as pd
import numpy as np
from datetime import datetime, timedelta

def load_sample_data(filepath='tweets.csv'):
    """
    Load tweets from CSV file instead of Twitter API
    """
    try:
        df = pd.read_csv(filepath)
        
        # Standardize column names
        column_mapping = {
            'text': 'tweet',
            'airline_sentiment': 'sentiment',
            'created_at': 'timestamp'
        }
        
        # Rename columns if they exist
        for old_col, new_col in column_mapping.items():
            if old_col in df.columns and new_col not in df.columns:
                df.rename(columns={old_col: new_col}, inplace=True)
        
        # Ensure required columns exist
        required_columns = ['tweet', 'sentiment', 'timestamp']
        for col in required_columns:
            if col not in df.columns:
                if col == 'timestamp':
                    # Generate timestamps
                    df['timestamp'] = pd.date_range(
                        end=datetime.now(), 
                        periods=len(df), 
                        freq='1min'
                    )
                elif col == 'sentiment':
                    # Will be analyzed later
                    df['sentiment'] = 'unknown'
        
        return df
    
    except FileNotFoundError:
        print("CSV file not found. Generating sample data...")
        return generate_sample_data()

def generate_sample_data(n=1000):
    """
    Generate sample tweets for testing
    """
    import random
    
    positive_tweets = [
        "Just got the iPhone 15! Absolutely loving it! 😍",
        "Best phone I've ever owned. The camera is incredible!",
        "Apple really outdid themselves this time. #iPhone15",
        "Upgraded from iPhone 12 - huge improvement!",
        "The battery life on this phone is amazing! 🔋"
    ]
    
    negative_tweets = [
        "iPhone 15 is way too expensive for what you get 😞",
        "Disappointed with the battery life. Expected more.",
        "Having issues with overheating. Not happy.",
        "The price increase is not justified. Overpriced!",
        "Regretting my purchase. Too many problems."
    ]
    
    neutral_tweets = [
        "Got the iPhone 15 today. Setting it up now.",
        "Switching from Android to iPhone. Let's see how it goes.",
        "iPhone 15 arrived. First impressions coming soon.",
        "Testing out the new features. Will report back.",
        "Comparing iPhone 15 with Samsung S23."
    ]
    
    tweets = []
    base_time = datetime.now() - timedelta(days=7)
    
    for i in range(n):
        sentiment = random.choices(
            ['positive', 'negative', 'neutral'],
            weights=[0.6, 0.2, 0.2]
        )[0]
        
        if sentiment == 'positive':
            tweet = random.choice(positive_tweets)
        elif sentiment == 'negative':
            tweet = random.choice(negative_tweets)
        else:
            tweet = random.choice(neutral_tweets)
        
        tweets.append({
            'tweet': tweet,
            'sentiment': sentiment,
            'timestamp': base_time + timedelta(minutes=i*10),
            'user': f'user_{random.randint(1000, 9999)}',
            'retweets': random.randint(0, 100),
            'likes': random.randint(0, 500)
        })
    
    return pd.DataFrame(tweets)

# Test the function
if __name__ == "__main__":
    df = load_sample_data()
    print(f"Loaded {len(df)} tweets")
    print(df.head())