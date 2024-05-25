# TLA-Match-Data
Approach for pulling and organising Challonge match data using the Challonge API

### Contents

*generate_base_data.py* can be used to pull data from Challonge and generate some labelled data. 
Tournament list to be pulled can be modified using the `PATTERNS` variable for dynamic generation and `tournament_names` for more specific tournament names. Does not include character data. Requires a Challonge API key to be set up in a .env file. 

*matches.csv* is one of the outputs of *generate_base_data.py*. It includes date, tournament, round, player_1, player_2, score (player_1-player_2)

*unique_players.csv* is the other output of *generate_base_data.py*. It could be used to assign mains to each unique player to be merged into *matches.csv* to get character matchup numbers. 
