import os
import requests
import json
import datetime
import pandas as pd
from dotenv import load_dotenv
from collections import defaultdict


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

def get_latest_tlg(latest_tlg=0):
    """Find the latest TLG tournament from Challonge"""
    index = latest_tlg + 1
    while True:
        tournament_name = f"ToughLoveGauntlet{index:03d}"
        tournament_data = make_api_request(f'tournaments/{tournament_name}')
        if tournament_data is None:
            break
        if tournament_data['tournament']['state'] == 'complete':
            latest_tlg = index
        index += 1
    return latest_tlg

def generate_tournament_names(start_tlg):
    """Generate tournament names dynamically"""
    latest_tlg = get_latest_tlg(start_tlg)
    return [f"ToughLoveGauntlet{i:03d}" for i in range(start_tlg + 1, latest_tlg + 1)]

def get_participants(tournament_name):
    """Get participants for a given tournament name"""
    return make_api_request(f'tournaments/{tournament_name}/participants')

def get_matches(tournament_name):
    """Get matches for a given tournament name"""
    return make_api_request(f'tournaments/{tournament_name}/matches')

def generate_player_dict(tournament_names, existing_players=None):
    """Generate player dictionary and Challonge ID key"""
    tla_players = defaultdict(lambda: defaultdict(int))
    if existing_players:
        tla_players.update(existing_players)
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
            if not tla_players[participant_challonge_id].get(participant_name): 
                tla_players[participant_challonge_id][participant_name] = 1
            else:
                tla_players[participant_challonge_id][participant_name] += 1

    return tla_players, challonge_id_key

def generate_match_data(tournament_names, challonge_id_key, existing_matches=None):
    """Fetch and parse match data"""
    all_matches = existing_matches if existing_matches is not None else []
    tournaments_not_found = []

    for tournament_name in tournament_names:
        matches = get_matches(tournament_name)
        if matches is None:
            tournaments_not_found.append(tournament_name)
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
    
    if tournaments_not_found:
        timestamp = datetime.datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
        file_name = f"tournaments_not_found_{timestamp}.txt"
        file_path = os.path.join("data", "raw", file_name)

        os.makedirs(os.path.dirname(file_path), exist_ok=True)

        with open(file_path, 'w') as file:
            file.write("Tournaments not found:\n")
            for tournament in tournaments_not_found:
                file.write(f"- {tournament}\n")

    return pd.DataFrame(all_matches)

def get_most_frequent_names(tla_players):
    """Get most frequently used name for each Challonge ID"""
    player_name_key = {}
    for challonge_id, names_dict in tla_players.items():
        most_frequent_name = max(names_dict, key=names_dict.get)
        player_name_key[challonge_id] = most_frequent_name
    return player_name_key

def fetch_match_data(data_dir="data/raw"):
    # Load existing data if available
    existing_matches = None
    existing_players = None
    try:
        existing_matches = pd.read_csv(f'{data_dir}/matches.csv').to_dict('records')
        with open(f'{data_dir}/tla_players.json', 'r') as f:
            existing_players = json.load(f)
    except FileNotFoundError:
        print("No existing data found. Starting from scratch.")

    # Get the latest processed TLG number
    start_tlg = 0
    if existing_matches:
        tlg_numbers = [int(t.split('ToughLoveGauntlet')[1]) for t in pd.DataFrame(existing_matches)['tournament']]
        start_tlg = max(tlg_numbers)

    # Generate tournament names
    tournament_names = generate_tournament_names(start_tlg)

    if not tournament_names:
        print("No new tournaments to process.")
        return

    # Generate players and matches
    tla_players, challonge_id_key = generate_player_dict(tournament_names, existing_players)
    matches_df = generate_match_data(tournament_names, challonge_id_key, existing_matches)

    # Get the most frequent names and replace IDs with names in DataFrame
    player_name_key = get_most_frequent_names(tla_players)
    matches_df.replace(player_name_key, inplace=True)

    # Save match data to CSV
    matches_df.to_csv(f'{data_dir}/matches.csv', index=False)

    # Save player data to json
    with open(f'{data_dir}/tla_players.json', 'w') as f:
        json.dump(tla_players, f, indent=4)

    print(f"Processed {len(tournament_names)} new tournaments.")

if __name__ == "__main__":
    # Variables
    load_dotenv()
    API_KEY = os.getenv("API_KEY")
    BASE_URL = 'https://api.challonge.com/v1/'

    fetch_match_data()
