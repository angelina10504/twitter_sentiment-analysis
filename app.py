# Create a new app.py file (this will be your main application)

from flask import Flask, render_template, jsonify, request
import pandas as pd
from textblob import TextBlob
from datetime import datetime, timedelta
import random
import re

app = Flask(__name__)
tweets_df = None

def clean_tweet(tweet):
    """Remove URLs, mentions, hashtags, and special characters"""
    tweet = re.sub(r'http\S+|www\S+|https\S+', '', tweet, flags=re.MULTILINE)
    tweet = re.sub(r'@\w+|#\w+', '', tweet)
    tweet = re.sub(r'[^\w\s]', '', tweet)
    return tweet.strip()

def analyze_sentiment(tweet):
    """Analyze sentiment using TextBlob"""
    analysis = TextBlob(clean_tweet(tweet))
    polarity = analysis.sentiment.polarity
    
    if polarity > 0.1:
        return 'positive', polarity
    elif polarity < -0.1:
        return 'negative', polarity
    else:
        return 'neutral', polarity

def generate_sample_tweets(brand_name="iPhone 15", n=1000):
    """Generate realistic sample tweets"""
    
    # Positive tweet templates
    positive = [
        f"Just got the {brand_name}! Absolutely loving it! 😍",
        f"Best phone ever! The {brand_name} camera is incredible! 📸",
        f"Apple really outdid themselves with {brand_name}. Amazing!",
        f"Upgraded to {brand_name} - huge improvement! Worth it 💰",
        f"The battery life on {brand_name} is amazing! 🔋",
        f"Finally got {brand_name}. Best decision ever! ⭐⭐⭐⭐⭐",
        f"{brand_name} display quality is stunning! 🌈",
        f"Face ID on {brand_name} works flawlessly! 👍",
        f"USB-C on {brand_name} is a game changer! ❤️",
        f"The speed on {brand_name} is incredible! 🚀"
    ]
    
    # Negative tweet templates
    negative = [
        f"{brand_name} is way too expensive 😞",
        f"Disappointed with {brand_name} battery life 😔",
        f"Having overheating issues with {brand_name} 🔥",
        f"Price of {brand_name} is not justified 💸",
        f"Regretting my {brand_name} purchase 😤",
        f"{brand_name} camera not as advertised 📷",
        f"Build quality of {brand_name} feels cheap 🤔",
        f"Software bugs on {brand_name} everywhere 😡",
        f"{brand_name} battery drains too quickly 🔋",
        f"Not worth upgrading to {brand_name} 👎"
    ]
    
    # Neutral tweet templates
    neutral = [
        f"Got the {brand_name} today. Setting it up.",
        f"Switching to {brand_name}. Let's see how it goes.",
        f"{brand_name} arrived. First impressions soon 📦",
        f"Testing {brand_name} features today.",
        f"Comparing {brand_name} with competitors 🤔",
        f"Just unboxed {brand_name} 🧵",
        f"Day 1 with {brand_name}. So far okay.",
        f"Trying out {brand_name} camera 📸",
        f"Setting up apps on {brand_name}",
        f"{brand_name} setup complete."
    ]
    
    tweets = []
    base_time = datetime.now() - timedelta(days=7)
    
    for i in range(n):
        # Weight: 58% positive, 15% negative, 27% neutral
        sentiment_type = random.choices(
            ['positive', 'negative', 'neutral'],
            weights=[0.58, 0.15, 0.27]
        )[0]
        
        if sentiment_type == 'positive':
            tweet_text = random.choice(positive)
        elif sentiment_type == 'negative':
            tweet_text = random.choice(negative)
        else:
            tweet_text = random.choice(neutral)
        
        tweets.append({
            'tweet': tweet_text,
            'timestamp': base_time + timedelta(minutes=i*10),
            'user': f'user_{random.randint(1000, 9999)}',
            'retweets': random.randint(0, 150),
            'likes': random.randint(0, 800)
        })
    
    return pd.DataFrame(tweets)

@app.route('/')
def index():
    """Main page"""
    return render_template('index.html')

@app.route('/analyze', methods=['POST'])
def analyze():
    """Analyze tweets endpoint"""
    global tweets_df
    
    try:
        data = request.get_json()
        search_term = data.get('search_term', 'iPhone 15')
        
        print(f"\n📊 Analyzing tweets for: {search_term}")
        
        # Generate sample tweets
        tweets_df = generate_sample_tweets(search_term, 1000)
        
        # Analyze sentiment
        sentiments = []
        scores = []
        
        for tweet in tweets_df['tweet']:
            sentiment, score = analyze_sentiment(tweet)
            sentiments.append(sentiment)
            scores.append(score)
        
        tweets_df['analyzed_sentiment'] = sentiments
        tweets_df['sentiment_score'] = scores
        
        # Calculate statistics
        sentiment_counts = tweets_df['analyzed_sentiment'].value_counts().to_dict()
        total = len(tweets_df)
        
        sentiment_percentages = {
            'positive': round(sentiment_counts.get('positive', 0) / total * 100, 1),
            'negative': round(sentiment_counts.get('negative', 0) / total * 100, 1),
            'neutral': round(sentiment_counts.get('neutral', 0) / total * 100, 1)
        }
        
        # Get sample tweets
        sample_tweets = {}
        for sentiment_type in ['positive', 'negative', 'neutral']:
            sentiment_tweets = tweets_df[tweets_df['analyzed_sentiment'] == sentiment_type]
            top_tweets = sentiment_tweets.nlargest(5, 'likes')['tweet'].tolist()
            sample_tweets[sentiment_type] = top_tweets if top_tweets else ['No tweets found']
        
        response = {
            'success': True,
            'total_tweets': total,
            'sentiment_counts': sentiment_counts,
            'sentiment_percentages': sentiment_percentages,
            'sample_tweets': sample_tweets,
            'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        }
        
        print(f"✅ Analysis complete!")
        print(f"   Positive: {sentiment_percentages['positive']}%")
        print(f"   Neutral: {sentiment_percentages['neutral']}%")
        print(f"   Negative: {sentiment_percentages['negative']}%\n")
        
        return jsonify(response)
    
    except Exception as e:
        print(f"❌ Error: {str(e)}")
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/get_timeline_data', methods=['GET'])
def get_timeline_data():
    """Get sentiment over time"""
    global tweets_df
    
    if tweets_df is None or tweets_df.empty:
        return jsonify({'error': 'No data available'}), 404
    
    try:
        tweets_df['hour'] = pd.to_datetime(tweets_df['timestamp']).dt.floor('H')
        timeline = tweets_df.groupby(['hour', 'analyzed_sentiment']).size().unstack(fill_value=0)
        
        response = {
            'timestamps': timeline.index.strftime('%m-%d %H:%M').tolist(),
            'positive': timeline.get('positive', pd.Series([0]*len(timeline))).tolist(),
            'negative': timeline.get('negative', pd.Series([0]*len(timeline))).tolist(),
            'neutral': timeline.get('neutral', pd.Series([0]*len(timeline))).tolist()
        }
        
        return jsonify(response)
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    print("\n" + "="*60)
    print("🐦 TWITTER SENTIMENT ANALYSIS DASHBOARD")
    print("="*60)
    print("\n📊 Starting server...")
    print("🌐 Open your browser and go to: http://127.0.0.1:5000")
    print("⌨️  Press Ctrl+C to stop\n")
    print("="*60 + "\n")
    
    app.run(debug=True, host='127.0.0.1', port=5000)

