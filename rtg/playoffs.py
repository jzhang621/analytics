import json

playoffs = [('CLE', 'DET'), ('BOS', 'CHI'), ('WAS', 'IND'), ('TOR', 'ATL'),
            ('GSW', 'DEN'), ('SAS', 'OKC'), ('HOU', 'MEM'), ('LAC', 'UTA')]


with open('pace_breakdown.json') as pace:
    pace_data = json.load(pace)

team_to_pace_data = {}
for team in pace_data:
    team_name = team['team_name']
    team_to_pace_data[team_name] = team


def parse_pace_data(team_pace_data):
    """
    Parse a dictionary of team pace data into components.
    """
    split_pace_data = {}
    above_pace = team_pace_data['above_pace']
    below_pace = team_pace_data['below_pace']

    total_games = above_pace['W'] + below_pace['W'] + above_pace['L'] + below_pace['L']
    total_wins = above_pace['W'] + below_pace['W']
    total_win_pct = total_wins / float(total_games)

    above_pace_win_pct = above_pace['W'] / float(above_pace['W'] + above_pace['L'])
    below_pace_win_pct = below_pace['W'] / float(below_pace['W'] + below_pace['L'])

    delta_below = round(below_pace_win_pct * total_games - total_wins, 2)
    delta_above = round(above_pace_win_pct * total_games - total_wins, 2)
    team_name = team_pace_data['team_name']
    deltas = {team_name: {'delta_wins_below': delta_below, 'delta_wins_above': delta_above}}
    print deltas
    return deltas


def parse_pace_data_for_all_teams():
    all_teams = []
    for team in team_to_pace_data:
        pace_data = team_to_pace_data[team]
        all_teams.append(parse_pace_data(pace_data))
    return all_teams


def parse_pace_data_for_playoff_teams():
    """

    """
    all_teams = []
    for teams in playoffs:
        team_a, team_b = teams
        matchup_data = {}
        pace_data_for_a = parse_pace_data(team_to_pace_data[team_a])
        pace_data_for_b = parse_pace_data(team_to_pace_data[team_b])
        matchup_data.update(pace_data_for_a)
        matchup_data.update(pace_data_for_b)
        all_teams.append(matchup_data)

    return all_teams

pace_data_for_playoff_teams = parse_pace_data_for_playoff_teams()

with open('playoff_pace_data.json', 'w') as playoff_pace_data:
    json.dump(pace_data_for_playoff_teams, playoff_pace_data)
