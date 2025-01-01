# Steam Reviews Sentiment Analysis

This project is dedicated to analyzing and visualizing user sentiment from Steam game reviews. The goal is to process the reviews, perform sentiment analysis, and display interactive visualizations to gain insights into public perceptions of various games. It leverages a combination of data cleaning, multithreading for faster processing, and sentiment scoring based on user reviews.

## Project Overview

In this repository, we explore the sentiment trends of Steam game reviews for games from 2020, using sentiment analysis to categorize reviews as positive, negative, or neutral. The project includes several key steps:

1. **Data Cleaning**: We filter the dataset to ensure that only English reviews are included, and that reviews are not empty and contain at least three characters.
2. **Sentiment Analysis**: We calculate sentiment scores based on the ratio of good to bad reviews, storing the results for faster future use.
3. **Visualization**: The sentiment data is visualized through interactive bar graphs to highlight which games have the most positive feedback.

The project also includes optimizations to handle large datasets efficiently, utilizing multithreading and caching to speed up data processing.

## Files in This Repository

- **`steam_reviews_sentiment_analysis.ipynb`**: The main Jupyter notebook file that contains the sentiment analysis workflow. This notebook processes the data, performs sentiment analysis, and generates visualizations for exploring the sentiment trends of Steam game reviews.
- **`largedata_reader.py`**: This Python file includes the `largedataframereader` function, which speeds up the data processing by leveraging multithreading. It filters the dataset for English reviews, non-empty entries, and reviews with a minimum length of three characters.
- **`game_scores_cache.csv`**: A CSV file that stores precomputed sentiment scores for each game. The cache helps avoid recomputing the sentiment scores every time the analysis is run.

## How to Use This Repository

### 1. **Dataset**
This project requires the **Steam Reviews 2021** dataset, which is too large to upload directly to GitHub. You can download it from Kaggle using the following link:

[Download the Steam Reviews 2021 dataset](https://www.kaggle.com/datasets/najzeko/steam-reviews-2021)

Once downloaded, place the dataset file (`steam_reviews.csv`) in the appropriate directory on your local machine for the analysis to work properly.

set df variable to the file path of the steam dataframe 






When running this program to see how it works and to look at the data the visualizations should look as follows 
but still run it so you can use the zoom in feature 

![image](https://github.com/user-attachments/assets/805ee9e9-b87c-498c-87ee-09f3459469e9)



![image](https://github.com/user-attachments/assets/72e90717-75d5-4fe7-876e-1688f87fa05b)



