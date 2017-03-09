from bs4 import BeautifulSoup
from urllib2 import urlopen
import json
import re
from cachetools import LRUCache
from collections import defaultdict

results_cache = LRUCache(maxsize=2000)


base_url = 'http://www.basketball-reference.com/teams/{0}/2017_games.html'
bball_ref_base_url = 'http://www.basketball-reference.com{0}'

def get_html(url):
    page = urlopen(url).read()
    return page

def parse_regular_season_games(html):
    team_page_html_parser = BeautifulSoup(html, 'html.parser')
    stats_table = team_page_html_parser.find('table', {'class': 'stats_table'}).find('tbody')
    game_results = stats_table.findAll('tr')

    pace_and_game_results = []
    for game in game_results:
        class_for_game_row = game.attrs.get('class')
        if class_for_game_row and 'thead' in class_for_game_row:
            continue
        columns = game.findAll('td')
        result = columns[6].text
        if not result:
            break

        box_score_link = bball_ref_base_url.format(columns[3].find('a', href=True)['href'])

        if box_score_link in results_cache:
            pace_for_game = results_cache[box_score_link]
        else:
            pace_for_game = parse_pace_from_box_score(box_score_link)
        pace_and_game_results.append((result, pace_for_game))
        print '{0}: {1}'.format(result, pace_for_game)

    return pace_and_game_results


def parse_pace_from_box_score(box_score_link):
    box_score_html = get_html(box_score_link)

    pace_string = 'data-stat="pace" >'
    pace_index = box_score_html.find(pace_string)

    if pace_index > -1:
        pace_html = box_score_html[pace_index:pace_index+30]
        pace_regex = '[0-9]{2,3}\.\d'

        pace_for_game = float(re.search(pace_regex, pace_html).group())

        results_cache.update({box_score_link: pace_for_game})
        return pace_for_game


def pace_and_game_to_win_loss(team_name, overall_pace, pace_and_game_results):

    info = {'team_name': team_name, 'above_pace': defaultdict(int), 'below_pace': defaultdict(int)}

    for game in pace_and_game_results:
        result, pace = game
        if pace > overall_pace:
            info['above_pace'][result] += 1
        else:
            info['below_pace'][result] += 1
    return info


with open('team_ratings.json', 'r') as team_data:
    data = json.load(team_data)

    all_teams = []
    for d in data:
        team_name = d['Team Name']
        pace = float(d['pace'])

        team_html = get_html(base_url.format(team_name))
        pace_and_game_results = parse_regular_season_games(team_html)
        pace_info = pace_and_game_to_win_loss(team_name, pace, pace_and_game_results)
        all_teams.append(pace_info)
        print pace_info


with open('pace_breakdown.json', 'w') as pace_breakdown:
    json.dump(all_teams, pace_breakdown)
