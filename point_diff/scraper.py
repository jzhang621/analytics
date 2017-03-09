import click
from bs4 import BeautifulSoup
from urllib2 import urlopen
import json

INDEX_TO_STAT_MAP = {
    8: 'team_pts',
    9: 'opp_pts',
    10: 'W',
    11: 'L'
}


base_url = 'http://www.basketball-reference.com/teams/{0}/2017_games.html'


def get_team_results_page_html(team_name):
    team_page_url = base_url.format(team_name)
    return urlopen(team_page_url).read()


def parse_team_results_page(team_page_html):
    team_page_html_parser = BeautifulSoup(team_page_html, 'html.parser')
    stats_table = team_page_html_parser.find('table', {'class': 'stats_table'}).find('tbody')
    game_results = stats_table.findAll('tr')

    game_info = [{'W': 0, 'L': 0}]
    for game in game_results:
        class_for_game_row = game.attrs.get('class')
        if class_for_game_row and 'thead' in class_for_game_row:
            continue

        game_info_dict = _parse_game_to_dict(game)
        if game_info_dict:
            game_info.append(game_info_dict)

    return game_info

def _parse_game_to_dict(game_html):

    game_data = {}
    for index, column in enumerate(game_html.findAll('td')):
        if index in INDEX_TO_STAT_MAP:

            if not column.text:
                return None

            stat_name = INDEX_TO_STAT_MAP[index]
            game_data[stat_name] = int(column.text)

    game_data['game_diff'] = game_data['team_pts'] - game_data['opp_pts']
    return game_data


def calculate_pt_diff_data(team_results_data):

    # initialize
    game_count = 1.0
    team_results_data[1]['running_diff'] = team_results_data[1]['game_diff']
    team_results_data[1]['per_game_pt_diff'] = team_results_data[1]['running_diff'] / game_count
    team_results_data[1]['total_team_pts'] = team_results_data[1]['team_pts']
    team_results_data[1]['total_opp_pts'] = team_results_data[1]['opp_pts']

    for index in range(2, len(team_results_data)):
        game_count += 1
        last_running_diff = team_results_data[index - 1]['running_diff']
        curr_diff = team_results_data[index]['game_diff']
        running_diff = last_running_diff + curr_diff

        team_results_data[index]['total_team_pts'] = team_results_data[index - 1]['total_team_pts'] + team_results_data[index]['team_pts']
        team_results_data[index]['total_opp_pts'] = team_results_data[index - 1]['total_opp_pts'] + team_results_data[index]['opp_pts']

        team_results_data[index]['running_diff'] = running_diff
        team_results_data[index]['per_game_pt_diff'] = round(running_diff / game_count, 3)

        team_results_data[index]['projected_pt_diff_wins'] = _calculate_projected_wins_from_pt_diff(team_results_data[index], game_count)

        wins = team_results_data[index]['W']
        team_results_data[index]['projected_total_wins'] = _calculate_projected_total_wins(wins, game_count)

        # print team_results_data

    return team_results_data


def _calculate_projected_wins_from_pt_diff(game_data, game_count):
    # total_pts = game_data['total_team_pts'] / game_count
    # opp_pts = game_data['total_opp_pts'] / game_count
    total_pts = game_data['total_team_pts']
    opp_pts = game_data['total_opp_pts']


    factor = 16.5
    return round(((total_pts ** factor) / (total_pts ** factor + opp_pts ** factor) * 82.0), 3)
    # return round(point_diff * 2.7 + 41, 3)


def _calculate_projected_total_wins(num_wins, game_count):

    win_pct = num_wins / game_count
    return round(win_pct * 82.0, 3)




@click.command()
# @click.option('--team', help='The team to get data for')
def main():

    with open('team_names.json', 'r') as team_names:
        all_teams = json.load(team_names)

        for team in all_teams:
            try:
                print 'getting data for team: {0}'.format(team)
                team_results = get_team_results_page_html(team)
                team_results_data = parse_team_results_page(team_results)
                pt_diff_data = calculate_pt_diff_data(team_results_data)
            except:
                print 'invalid team name: ', team
                continue

            with open('team_data/{0}.json'.format(team), 'w') as team_data:
                json.dump(pt_diff_data, team_data)


if __name__ == '__main__':
    main()


