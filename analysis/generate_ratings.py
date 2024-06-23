import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

from skelo.model.elo import EloEstimator
from skelo.model.glicko2 import Glicko2Estimator


# Read the dataset
# This needs to be run after generate_base_data.py
data = pd.read_csv('matches.csv')

# Extract individual scores and handle forfeits/dqs
def extract_scores(score):
    # Use only the first score if multiple scores are present
    # Multiple scores probably
    first_score = score.split(',')[0]
    # This split should be replaced by a regex
    if first_score == "0--1":
        return 0, -1
    elif first_score == "-1-0":
        return -1, 0
    else:
        try:
            return int(first_score.split('-')[0]), int(first_score.split('-')[1])
        except ValueError:
            return None, None  # Handle the case where the score is invalid

# Drop rows with missing values
data.dropna(subset=['score'], inplace=True)

# Apply the extract_scores function and expand the result into two columns
data[['player_1_score', 'player_2_score']] = data['score'].apply(lambda x: pd.Series(extract_scores(x)))

# Drop rows where the score extraction resulted in invalid scores
data.dropna(subset=['player_1_score', 'player_2_score'], inplace=True)

# Determine the winner and loser based on the scores
def determine_winner_loser(row):
    player_1 = row['player_1']
    player_2 = row['player_2']
    score1 = row['player_1_score']
    score2 = row['player_2_score']
    
    if score1 == -1:
        return player_2, player_1  # Player 2 wins by forfeit/dq
    elif score2 == -1:
        return player_1, player_2  # Player 1 wins by forfeit/dq
    elif score1 > score2:
        return player_1, player_2  # Player 1 wins
    else:
        return player_2, player_1  # Player 2 wins

data[['winner_name', 'loser_name']] = data.apply(determine_winner_loser, axis=1, result_type="expand")
data['unix_time'] = pd.to_datetime(data['date'], utc=True).astype(int) // 10**9
data['date'] = pd.to_datetime(data['date'], utc=True).dt.tz_localize(None)

# Select the desired columns
organised_data = data[['unix_time', 'tournament', 'player_1', 'player_2', 'winner_name', 'loser_name']]
organised_data = data[['date', 'tournament', 'player_1', 'player_2', 'winner_name', 'loser_name']]

# Data is organised as winner, loser
labels = len(organised_data) * [1]

elo_model = EloEstimator(
    key1_field="winner_name",
    key2_field="loser_name",
    # timestamp_field="unix_time",
    timestamp_field="date",
    # initial_time=1609477200,
    initial_time=np.datetime64('2021', 'Y'),
).fit(organised_data, labels)

glicko_model = Glicko2Estimator(
    key1_field="winner_name",
    key2_field="loser_name",
    # timestamp_field="unix_time",
    timestamp_field="date",
    # initial_time=1609477200,
    initial_time=np.datetime64('2021', 'Y'),
).fit(organised_data, labels)

plt.style.use('tableau-colorblind10')

#  Retrieve the fitted Elo ratings from the model & plot them
ratings_est = elo_model.rating_model.to_frame()
elo_ts_est = ratings_est.pivot_table(index='valid_from', columns='key', values='rating').ffill()

elo_idx = elo_ts_est.iloc[-1].sort_values().index[-10:]
elo_ax = elo_ts_est.loc[:, elo_idx].plot(figsize=(18, 8), title='Top 10 Elo ratings as of TLG 159\nTLG matches only')
elo_ax.set_xlabel('Date')
elo_ax.set_ylabel('Rating')
elo_ax.legend(title='Player', loc='upper left')

# Save the plot as an image file
plt.savefig('elo_ratings_plot.png', dpi=300)

# # Glicko ratings need a bit of work due to some big first movers that makes the data look weird
# #  Retrieve the fitted glicko ratings from the model & plot them
# ratings_est = glicko_model.rating_model.to_frame()
# ratings_est['rating_only'] = ratings_est['rating'].str[0]
# glicko_ts_est = ratings_est.pivot_table(index='valid_from', columns='key', values='rating_only').ffill()

# glicko_idx = glicko_ts_est.iloc[-1].sort_values().index[-5:]
# glicko_ax = glicko_ts_est.loc[:, glicko_idx].plot(figsize=(10, 6), title='Top 5 glicko Ratings Over Time')
# glicko_ax.set_xlabel('Date')
# glicko_ax.set_ylabel('Rating')
# glicko_ax.legend(title='Player', loc='upper left')

# # Save the plot as an image file
# plt.savefig('glicko_ratings_plot.png', dpi=300)
