import re
import json
import pandas as pd
from collections import Counter
from yt_dlp import YoutubeDL


def identify_tournaments(df, coverage_threshold=0.8, top_active_threshold=0.2):
    # Get unique players
    all_players = set(df['player_1'].unique()) | set(df['player_2'].unique())
    total_players = len(all_players)

    # Count player appearances
    player_appearances = Counter(df['player_1']) + Counter(df['player_2'])
    
    # Identify top x% most active players
    sorted_players = sorted(player_appearances.items(), key=lambda x: x[1], reverse=True)
    top_players = set([player for player, _ in sorted_players[:int(total_players * top_active_threshold)]])

    # Initialize variables
    selected_tournaments = set()
    covered_players = set()
    
    # Sort tournaments by number of unique players
    tournament_players = df.groupby('tournament').agg({
        'player_1': lambda x: set(x),
        'player_2': lambda x: set(x)
    })
    tournament_players['unique_players'] = tournament_players.apply(lambda row: row['player_1'] | row['player_2'], axis=1)
    tournament_players['player_count'] = tournament_players['unique_players'].apply(len)
    sorted_tournaments = tournament_players.sort_values('player_count', ascending=False)

    # Select tournaments
    for tournament, row in sorted_tournaments.iterrows():
        if (len(covered_players) / total_players >= coverage_threshold and 
            top_players.issubset(covered_players)):
            break
        
        selected_tournaments.add(tournament)
        covered_players |= row['unique_players']

    return list(selected_tournaments)


YDL_OPTIONS = {
    'noplaylist': 'True',
    'format': 'bestvideo[height>=480]+bestaudio/best[height>=480]'
}

def search_youtube(arg):
    with YoutubeDL(YDL_OPTIONS) as ydl:
        try:
            video = ydl.extract_info(f"ytsearch:{arg}", download=False)['entries'][0]
        except Exception as e:
            print(f"An error occurred while searching for '{arg}': {str(e)}")
            return None
        
        # Check if the video is uploaded by 'shygybeats'
        if video.get('uploader', '').lower() != '` shygybeats `':
            print(f"Skipping video '{video.get('title')}' - not uploaded by shygybeats")
            return None

        # Check if 'modded' is in the title
        if 'modded' in video.get('title', '').lower():
            print(f"Skipping video '{video.get('title')}' - contains 'modded' in title")
            return None

        # Check if the video has at least 480p quality
        formats = video.get('formats', [])
        has_480p_or_better = any(
            f.get('height') is not None and f.get('height') >= 480 
            for f in formats
        )
        
        if not has_480p_or_better:
            print(f"Skipping video '{video.get('title')}' due to low quality")
            return None

        # Extract relevant information
        cleared_data = {
            'channel': video.get('uploader'),
            'title': video.get('title'),
            'video_url': video.get('webpage_url'),
            'duration': video.get('duration'),
            'upload_date': video.get('upload_date'),
        }
        return cleared_data

def format_string(s):
    # Insert space before uppercase letters that are followed by lowercase letters
    s = re.sub(r'(?<!^)(?=[A-Z][a-z])', ' ', s)
    # Insert space before digits
    s = re.sub(r'(?<=\D)(?=\d)', ' ', s)
    return s

def generate_youtube_info(tournaments):
    video_info_list = []
    for tournament in tournaments:
        # Create search query
        query = format_string(tournament)

        # Search YouTube
        video_info = search_youtube(query)
        
        if video_info:
            video_info['tournament'] = tournament
            video_info_list.append(video_info)
    
    return video_info_list


if __name__ == "__main__":
    df = pd.read_csv('data/raw/matches.csv')
    # tournaments = identify_tournaments(df)
    tournaments = list(set(df['tournament']))
    youtube_info = generate_youtube_info(tournaments)

    # Save results to a file
    output_file = 'data/raw/tlg_youtube_urls.json'
    with open(output_file, 'w') as f:
        json.dump(youtube_info, f, indent=2)

    print(f"Results have been saved to {output_file}")
