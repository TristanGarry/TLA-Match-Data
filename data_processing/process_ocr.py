import pandas as pd
from collections import defaultdict

def clean_and_aggregate_data(csv_file):
    # Read the CSV file
    df = pd.read_csv(csv_file, dtype=str)

    # Initialize a dictionary to store matchup information
    matchups = defaultdict(lambda: {'p1_chars': defaultdict(int), 'p2_chars': defaultdict(int), 'occurrences': 0})

    # Process each row in the dataframe
    for _, row in df.iterrows():
        p1_name = str(row['player_1_name'])
        p2_name = str(row['player_2_name'])
        p1_char = str(row['player_1_character'])
        p2_char = str(row['player_2_character'])

        # Skip rows where both player names are not properly detected
        if len(p1_name) <= 1 or len(p2_name) <= 1:
            continue

        matchup_key = (p1_name, p2_name)
        matchup = matchups[matchup_key]

        # Update character counts and occurrence
        if p1_char != 'Unknown':
            matchup['p1_chars'][p1_char] += 1
        if p2_char != 'Unknown':
            matchup['p2_chars'][p2_char] += 1
        matchup['occurrences'] += 1

    # Process the aggregated data
    results = []
    for (p1_name, p2_name), matchup in matchups.items():
        p1_char = max(matchup['p1_chars'], key=matchup['p1_chars'].get, default='Unknown')
        p2_char = max(matchup['p2_chars'], key=matchup['p2_chars'].get, default='Unknown')
        
        # Only include matchups with a minimum number of occurrences and known characters
        if matchup['occurrences'] >= 5 and p1_char != 'Unknown' and p2_char != 'Unknown':
            results.append({
                'player_1_name': p1_name,
                'player_1_character': p1_char,
                'player_2_name': p2_name,
                'player_2_character': p2_char,
                'occurrence': matchup['occurrences']
            })

    # Create a dataframe from the results and sort it
    result_df = pd.DataFrame(results)
    result_df = result_df.sort_values('occurrence', ascending=False)

    return result_df


if __name__ == "__main__":
    # Use the function
    cleaned_data = clean_and_aggregate_data('output.csv')

    # Display the results
    print(cleaned_data)

    # Optionally, save the cleaned data to a new CSV file
    cleaned_data.to_csv('cleaned_matchups.csv', index=False)
