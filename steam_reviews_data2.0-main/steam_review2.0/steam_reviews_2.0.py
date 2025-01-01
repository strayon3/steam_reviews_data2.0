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
    #path for csv here for datset
    df_path = "C:/Users/wills/OneDrive/Desktop/steam_csv/steam_reviews.csv"
    dataframe = parallel_read_csv(df_path)

    #validate the results
    print(dataframe.head())
    #converts from a polars object to a pandas object
    dataframe = dataframe.to_pandas()

    for i in dataframe["app_name"]:
        if i not in game_titles:
            game_titles.append(i)


#put your wordlist here the path to that file 
#look reviews and determin sentiments
with open("C:/Users/wills/OneDrive/Desktop/worddlists/positive-words.txt", "r") as f:
   good_keywords = [line.strip() for line in f.readlines()]

#load bad wordlist
with open("C:/Users/wills/OneDrive/Desktop/worddlists/negative-words.txt","r") as f:
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
            print(f"Scores after chunk {i + 1}: {game_scores}")
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

"""take the sentiment scores and show graph for good and bad
side by side per game """

#create the graphs 
#make bars and graph larger to hard to read 
#put grap into ascending order by good rating or in general what ever is easiest 
fig = px.bar(
        x=games,
        y=[good_reviews,bad_reviews],
        labels={"x":"Game", "y":"Review Count"}, #Axis labels
        title="Good vs. Bad Reviews per Game",
        barmode="group"  #grouped bars for comparison
    )

#display the figure
fig.show()

#calculate sentiment percent for each game
def calculate_percents(game_scores):
     sentiment_results = {}

     for game, scores in game_scores.items():
          total_reviews = scores["Good"] + scores["Bad"]

          if total_reviews > 0:
               sentiment_score = (scores["Good"] - scores["Bad"]) / total_reviews
               sentiment_results[game] = {
                    "Sentiment Score": round(sentiment_score, 2),
                    "Good": scores["Good"],
                    "Bad": scores["Bad"]
               }
          else:
               sentiment_results[game] = {
                    "Sentiment Score": 0,
                    "Good": scores["Good"],
                    "Bad": scores["Bad"]
               }
     return sentiment_results

#call calculate_percents function and store the results 
sentiment_scores = calculate_percents(game_sentiment)
#convert percents to a dict of each game for graph 
santiment_data = [
    {"Game":games, "Sentiment Percent": data["Sentiment Score"]}
    for game,data in sentiment_scores.items()
]
"""above breaks the sentiment scores into percents the closer to
pos number the higher the good sentiment
further below 1 is higher bad sentiment 
show it on a graph for break down """

#values are not being handed to this properly find out why need a bigger screen for it to see what vales
#are being passed 
#create the graph for the percent scores 
fig1 = px.bar(
    sentiment_scores,
    x="app_name",
    y="Sentiment Score",
    title="Game Sentiment Percentages",
    labels={"Sentiment Score": "Sentiment Score", "Game": "Game Title"},
    color="Sentiment Score",  # Adds color to the bars based on the score
    color_continuous_scale="RdYlGn"  # Green for positive, red for negative
)

fig1.show()




#goal for tomorrow 
#We are almost done fix these issues and its ready 
#For jupyter notbook

#Fix size of first graph bars to small and is cutting off
#fix the second graph values not right throwing error 
#will be as long as other so make size the same 

# do these and we are done it should be ready 