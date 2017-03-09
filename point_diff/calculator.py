import click
import json


def calculate_optimal_line(team_name):

    with open('team_data/{0}.json'.format(team_name), 'r') as team_games:
        team_games = json.load(team_games)
        current_game = len(team_games) + 1
        current_wins = team_games[-1]['W']

        max_overplay_ratio = -10000
        max_underplay_ratio = -10000

        keep_overplay_info = '{0}|None'.format(team_name)
        keep_underplay_info = '{0}|None'.format(team_name)
        count = 20
        for game in team_games[20:]:
            projected_record = game['projected_total_wins'] * (current_game / 82.0)
            projected_pt_diff_wins = game['projected_pt_diff_wins'] * (current_game / 82.0)

            # outplaying point differential
            if current_wins > projected_pt_diff_wins and projected_record > projected_pt_diff_wins:
                wins_above_pt_diff = current_wins - projected_pt_diff_wins
                record_above_pt_diff = projected_record - projected_pt_diff_wins
                overplay_ratio = record_above_pt_diff / wins_above_pt_diff
                overplay_info = "{0}|{1}: {2}/{3}={4}".format(team_name, count, record_above_pt_diff, wins_above_pt_diff, overplay_ratio)
                if overplay_ratio > max_overplay_ratio:
                    max_overplay_ratio = overplay_ratio
                    keep_overplay_info = overplay_info

            # underplaying point differential
            if current_wins < projected_pt_diff_wins and projected_record < projected_pt_diff_wins:
                wins_below_pt_diff = projected_pt_diff_wins - current_wins
                record_below_pt_diff = projected_pt_diff_wins - projected_record
                underplay_ratio = record_below_pt_diff / wins_below_pt_diff
                underplay_info = "{0}|{1}: {2}/{3}={4}".format(team_name, count, record_below_pt_diff, wins_below_pt_diff, underplay_ratio)
                if underplay_ratio > max_underplay_ratio:
                    max_underplay_ratio = underplay_ratio
                    keep_underplay_info = underplay_info
            count += 1


        if 'None' not in keep_overplay_info:
            print keep_overplay_info
        # if 'None' not in keep_underplay_info:
            # print keep_underplay_info
        # print



@click.command()
# @click.option('--team', help='The team to get data for')
def main():

    with open('team_names.json', 'r') as team_names:
        all_teams = json.load(team_names)

        for team in all_teams:
            calculate_optimal_line(team)


if __name__ == '__main__':
    main()
