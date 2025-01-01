import pandas as pd
import plotly.express as px
from concurrent.futures import ThreadPoolExecutor as te
import logging
import os
import csv
import gc
#These below are imported functions of self creation
from largedata_reader import parallel_read_csv
from largedata_reader import process_game_chunk
from largedata_reader import merge_scores



#we are going to be looking at tsteam reviews and applying sentiment analysis 
#on them for game in the steam store in either 2020 

#File sentiment scores will be cahced to its to help not have to recompute the sentiment scores every time 
Cache_file = "game_scores_cache.csv"


game_titles = []

if __name__ == '__main__':
    df_path = "c:/Users/stray/Desktop/portfolioDatasets/datasets/steam_reviews.csv"
    dataframe = parallel_read_csv(df_path)

    #validate the results
    print(dataframe.head())
    #converts from a polars object to a pandas object
    dataframe = dataframe.to_pandas()

    for i in dataframe["app_name"]:
        if i not in game_titles:
            game_titles.append(i)


#look reviews and determin sentiments
with open("c:/Users/stray/Desktop/game_reviews_wordlist/positive_sentiment_words.txt", "r") as f:
   good_keywords = [line.strip() for line in f.readlines()]

#load bad wordlist
with open("c:/Users/stray/Desktop/game_reviews_wordlist/negative_sentiment_words.txt","r") as f:
    bad_keywords = [line.strip() for line in f.readlines()]


def analyze_review(dataframe, game_titles, good_keywords, bad_keywords):
    #check if cache file exists
    if os.path.exists(Cache_file):
        print("Cache file found, loading sentiment scores...........")
        return load_scores_from_csv(Cache_file)
    
    logging.info("No cache file found, starting sentiment analysis..........")
    #initialize the game scores
    game_scores = {title:{"Good":0, "Bad":0} for title in game_titles}
    chunk_size = 100000

    print(f"Chunk size set to {chunk_size} reviews per batch..")

    good_keywords_set = set(good_keywords)
    bad_keywords_set = set(bad_keywords)

    #processs in chunks 
    chunks = (dataframe[i:i+chunk_size] for i in range(0, len(dataframe), chunk_size))
    with te() as executor:
        for i,chunk_results in enumerate(
            executor.map(
                lambda chunk: process_game_chunk(chunk, good_keywords_set,
                                 bad_keywords_set, game_scores),chunks
            )
        ):
            print(f"Processed {i + 1} chunks of reviews")
            merge_scores(chunk_results, game_scores)
            logging.debug(f"Scores after chunk {i + 1}: {game_scores}")
            gc.collect() # free memory to make sure no overflows happen 

    print("Saving computed game scores to CSV cache file")
    save_scores_to_csv(game_scores, Cache_file)

    print("Sentiment analysis completed successfully.")
    return game_scores

def load_scores_from_csv(filepath):
    """Load sentiment scores from a CSV file."""
    scores = {}
    with open(filepath, mode="r") as file:
        reader = csv.DictReader(file)
        for row in reader:
            scores[row["Title"]] = {"Good": int(row["Good"]), "Bad": int(row["Bad"])}
            print("Successfully loaded game scores from cache.")
    return scores

def save_scores_to_csv(game_scores, filepath):
    """Save sentiment scores to a CSV file."""
    with open(filepath, mode="w", newline="", encoding="utf-8") as file:
        writer = csv.writer(file)
        writer.writerow(["Title", "Good", "Bad"])
        for title, counts in game_scores.items():
            writer.writerow([title, counts["Good"], counts["Bad"]])
            print(f"Game scores saved to cache file: {filepath}")





game_sentiment = analyze_review(dataframe,game_titles,good_keywords,bad_keywords)
games = list(game_sentiment.keys())
good_reviews = [game_sentiment[game]["Good"] for game in games]
bad_reviews = [game_sentiment[game]["Bad"] for game in games]
