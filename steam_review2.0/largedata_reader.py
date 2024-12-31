import pandas as pd 
import polars as ppl
from concurrent.futures import ThreadPoolExecutor as te
import gc
import logging
from collections import defaultdict

#configure logging for backgorund processes
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")

def parallel_read_csv(file_path):
     """
    Read a large CSV file in parallel using chunks and process each chunk.
    
    Args:
    - file_path: Path to the CSV file
    - chunk_size: Size of the chunks to read at once (default: 999999)
    
    Returns:
    - A concatenated dataframe containing the processed data
    """
     #Lazy scan the csv file 
     dataframe = ppl.scan_csv(file_path).select([
          ppl.col("app_name"),
          ppl.col("language"),
          ppl.col("review")
     ]).filter(
          (ppl.col("language") == "english") &
          (ppl.col("review").is_not_null())&
          (ppl.col("review") !=  "") 
          
     )

     #dataframe = ppl.scan_csv(file_path, with_column_names=True, n_rows=chunk_size)

     results = dataframe.collect()

     
    
    #clean up memory for speed nothing else 
     gc.collect()

     return results


def process_game_chunk(chunk, good_keywords,bad_keywords,game_scores):
     """Process a single chunk of the dataset"""
     logging.info("Starting processing a chunk of reviews")
     local_scores = defaultdict(lambda: {"Good" : 0, "Bad" : 0})

     for _ , row in chunk.itterrows():
          title = row["app_name"]
          review = row["review"].lower().split() #tokenize review into words
          if title in game_scores: #Process only known game titles 
               logging.debug(f"Processing review for {title}")

               good_count = sum([1 for word in review if word in good_keywords])
               bad_count = sum([1 for word in review if word in bad_keywords])

               #Update local scores for the game 
               local_scores[title]["Good"] += good_count
               local_scores[title]["Bad"] += bad_count

               logging.info(f"Finished Processing {title}. Scores: {local_scores[title]}")

     logging.info("Completed processing chunk.")
     return local_scores

def merge_scores(local_scores, game_scores):
     '''Merge local scores into the main scores.'''
     logging.info("Merging local scores into global game scores.")
     for title, scores in local_scores.items():
          game_scores[title]["Good"] += scores["Good"]
          game_scores[title]["Bad"] += scores["Bad"]
     logging.info("Scores merged successfully.")

     