import os
import requests
import pandas as pd
import numpy as np
from dotenv import load_dotenv
from collections import defaultdict

# Variables
load_dotenv()
API_KEY = os.getenv("API_KEY")
BASE_URL = 'https://api.challonge.com/v1/'

# Patterns for dynamic tournament name generation
PATTERNS = [("ToughLoveGauntlet", 1, 159)]

def generate_tournament_names(patterns):
    """Generate tournament names dynamically"""
    tournament_names = []
    for prefix, start, end in patterns:
        num_length = 3 if prefix == "ToughLoveGauntlet" else 1
        for i in range(start, end + 1):
            tournament_names.append(f"{prefix}{i:0{num_length}}")
    return tournament_names

def make_api_request(endpoint):
    """Make API request to Challonge"""
    url = f'{BASE_URL}{endpoint}.json?api_key={API_KEY}'
    try:
        response = requests.get(url, headers={'User-Agent': 'Mozilla/5.0'})
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        print(f"API request error: {e}")
        return None

def get_participants(tournament_name):
    """Get participants for a given tournament name"""
    return make_api_request(f'tournaments/{tournament_name}/participants')

def get_matches(tournament_name):
    """Get matches for a given tournament name"""
    return make_api_request(f'tournaments/{tournament_name}/matches')

def generate_player_dict(tournament_names):
    """Generate player dictionary and Challonge ID key"""
    tla_players = defaultdict(lambda: defaultdict(int))
    challonge_id_key = {}

    for tournament_name in tournament_names:
        participants = get_participants(tournament_name)
        if participants is None:
            print(f"Could not get participants for {tournament_name}")
            continue

        for participant in participants:
            participant_data = participant['participant']
            participant_challonge_id = str(participant_data['challonge_user_id'])
            participant_tournament_id = str(participant_data['id'])
            participant_name = participant_data['name']

            challonge_id_key[participant_tournament_id] = participant_challonge_id
            tla_players[participant_challonge_id][participant_name] += 1

    return tla_players, challonge_id_key

def generate_match_data(tournament_names, challonge_id_key):
    """Fetch and parse match data"""
    all_matches = []

    for tournament_name in tournament_names:
        matches = get_matches(tournament_name)
        if matches is None:
            print(f"Could not find match data for {tournament_name}")
            continue

        for match in matches:
            match_data = match['match']
            match_info = {
                'date': match_data['created_at'],
                'tournament': tournament_name,
                'round': str(match_data['round']),
                'player_1': str(challonge_id_key.get(str(match_data['player1_id']), str(match_data['player1_id']))),
                'player_2': str(challonge_id_key.get(str(match_data['player2_id']), str(match_data['player2_id']))),
                'score': match_data['scores_csv']
            }
            all_matches.append(match_info)

    return pd.DataFrame(all_matches)

def get_most_frequent_names(tla_players):
    """Get most frequently used name for each Challonge ID"""
    player_name_key = {}
    for challonge_id, names_dict in tla_players.items():
        most_frequent_name = max(names_dict, key=names_dict.get)
        player_name_key[challonge_id] = most_frequent_name
    return player_name_key

def main():
    # Generate tournament names
    tournament_names = generate_tournament_names(PATTERNS)

    # Generate players and matches
    tla_players, challonge_id_key = generate_player_dict(tournament_names)
    matches_df = generate_match_data(tournament_names, challonge_id_key)

    # Get the most frequent names and replace IDs with names in DataFrame
    player_name_key = get_most_frequent_names(tla_players)
    matches_df.replace(player_name_key, inplace=True)

    # Save match data to CSV
    matches_df.to_csv('matches.csv', index=False)

    # Generate and save unique players list to CSV
    unique_players = np.unique(matches_df[["player_1", "player_2"]].values)
    np.savetxt("unique_players.csv", unique_players, delimiter=",", fmt="%s")

if __name__ == "__main__":
    main()
