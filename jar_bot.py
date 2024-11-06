import tweepy
import os
import time
from dotenv import load_dotenv

# Load API keys from .env file
load_dotenv()

API_KEY = os.getenv("API_KEY")
API_SECRET = os.getenv("API_SECRET")
ACCESS_TOKEN = os.getenv("ACCESS_TOKEN")
ACCESS_SECRET = os.getenv("ACCESS_SECRET")
BEARER_TOKEN = os.getenv("BEARER_TOKEN")

# Authenticate to Twitter API v2
api_v2 = tweepy.Client(
    bearer_token=BEARER_TOKEN,
    consumer_key=API_KEY,
    consumer_secret=API_SECRET,
    access_token=ACCESS_TOKEN,
    access_token_secret=ACCESS_SECRET
)

# Function to handle mentions and respond
def respond_to_mentions_v2(last_seen_id=None):
    try:
        user_id = api_v2.get_me().data.id

        params = {
            "id": user_id,
            "max_results": 5  # Fetch up to 5 mentions
        }
        if last_seen_id:
            params["since_id"] = last_seen_id  # Only fetch mentions after the last seen ID

        response = api_v2.get_users_mentions(**params)
        mentions = response.data

        if mentions:
            for mention in reversed(mentions):
                print(f"New mention from Tweet ID {mention.id}: {mention.text}")
                if "#jarbot" in mention.text.lower():
                    print("Responding to mention...")
                    api_v2.create_tweet(
                        text=f"@{mention.author_id} Thanks for the mention! 😊 #JarBot",
                        in_reply_to_tweet_id=mention.id
                    )
                    last_seen_id = mention.id
        else:
            print("No new mentions found.")
    except tweepy.errors.TooManyRequests as e:
        print("Rate limit exceeded. Please wait 15 minutes before checking again.")
    except tweepy.errors.TweepyException as e:
        print(f"Error responding to mentions: {e}")
    return last_seen_id

# Manage last_seen_id
def get_last_seen_id(file_name):
    try:
        with open(file_name, "r") as f:
            return f.read().strip()
    except FileNotFoundError:
        return None

def set_last_seen_id(last_seen_id, file_name):
    with open(file_name, "w") as f:
        f.write(str(last_seen_id))

if __name__ == "__main__":
    FILE_NAME = "last_seen_id.txt"

    # Track last seen mention ID
    last_seen_id = get_last_seen_id(FILE_NAME)

    while True:  # Adjust loop frequency
        print("Checking for new mentions...")
        last_seen_id = respond_to_mentions_v2(last_seen_id)
        set_last_seen_id(last_seen_id, FILE_NAME)
        print("Sleeping for 10 minutes...")
        time.sleep(600)  # Wait for 10 minutes before checking again.

