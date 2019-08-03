# Import dependencies
import tweepy
import pandas as pd
import os
import pathlib
from api_keys import API_key, secret_key, access_token, secret_token

# Set authorization for querying twitter API using tweepy
auth = tweepy.OAuthHandler(API_key, secret_key)
auth.set_access_token(access_token, secret_token)
api = tweepy.API(auth, wait_on_rate_limit=True)


def get_tweets(screen_name, since_id):
    """Queries API for tweets based on given search and date parameters.
    Returns list of search result objects"""

    print(f"Querying tweets for {screen_name}...")

    if since_id == 0:
        tweets = tweepy.Cursor(api.user_timeline,
                           id=screen_name,
                           tweet_mode='extended').items(1000)

    else:
        # Query for tweets from given screen_name since last query
        tweets = tweepy.Cursor(api.user_timeline,
                            id=screen_name,
                            since_id=since_id,
                            tweet_mode='extended').items(1000)

    return tweets


def convert_tweets(tweets):
    """Extracts desired tweet attributes into returned dataframe"""

    tweet_list = []
    for tweet in tweets:
        tweet_dict = {"ID": tweet.id_str,
                      "Date": tweet.created_at,
                      "Text": tweet.full_text,
                      "Retweet": tweet.retweet_count,
                      "Favorite": tweet.favorite_count}
        tweet_list.append(tweet_dict)

    tweet_df = pd.DataFrame(tweet_list)

    return(tweet_df)


def save_tweets(tweet_df, candidate_name, end_date):
    """Saves dataframe as csv"""

    filename = f"{candidate_name}_user_{end_date}.csv"
    tweet_df.to_csv(os.path.join("data", filename), index=False, header=True)

    print(f"Saved tweets to csv for {candidate_name}.")


def main():
    """Saves tweets from candidates since last query into csvs"""

    # Create dictionary of Candidates
    key = ["Biden", "Sanders", "Warren", "Harris"]
    value = ["@JoeBiden", "@BernieSanders", "@ewarren", "@KamalaHarris"]
    candidates = dict(zip(key, value))

    for key in candidates.keys():

        # Check to see if tweets have already been queried and saved
        file = pathlib.Path(f"data/{key}_user.csv")
        if file.exists():

            # Convert tweets to dataframe and set last tweet id
            tweet_df = pd.read_csv(file)
            since_id = tweet_df["ID"].max()

        # If no saved tweets, create empty dataframe and initialize tweet id
        else:
            since_id = 0
            tweet_df = pd.DataFrame(
                columns=["ID", "Date", "Text", "Retweet", "Favorite"])

        # Get tweets and convert to dataframe
        tweets = get_tweets(candidates[key], since_id)
        new_df = convert_tweets(tweets)

        # Append new tweets to old and save to csv
        tweet_df = tweet_df.append(new_df, ignore_index=True, sort=True)
        tweet_df.to_csv(file, index=False, header=True)
        print(f"Saved tweets to csv for {key}.")


main()
