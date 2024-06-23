# TLA-Match-Data

Approach for pulling and organising TLA match data.

WIP I'm changing this all to be automated to run but temporarily breaking it in the process.

## Roadmap

### Target state 

Two microdatasets

* Main release
    * Fields: date, tournament, tournament_series, round, player_1, player_2, score, player_1_character, player_2_character, player_1_score, player_2_score, patch
    * Built using Challonge match data, patch data, manually coded match data, manually coded solo character mains
    * Character data either manually coded or using solo mains
* Experimental release
    * Fields: date, tournament, tournament_series, round, player_1, player_2, score, player_1_character, player_2_character, player_1_score, player_2_score, patch
    * Built using Challonge match data, patch data, manually coded match data, manually coded solo character mains, OCR character data, modelled character data
    * Modelled character data to fill in any matches not covered by other sources 
    * Character data quality hierarchy: manually coded matches > manually coded solo character mains > OCR match data > modelled character data

Ten analysis datasets
* Elo over time (TLG only)
* Elo over time (all competitions)
* Glicko2 over time (TLG only)
* Glicko2 over time (all competitions)
* Character matchup charts
    * Rice
    * Noodle
    * Beef
    * Pork
    * Onion
    * Garlic

Auxiliary datasets

* TLA players and aliases
* TLG youtube links
* Model performance 

