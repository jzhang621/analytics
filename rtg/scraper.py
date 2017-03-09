from collections import defaultdict
import re

from bs4 import BeautifulSoup
from urllib2 import urlopen
import json

TEAM_RATINGS = defaultdict(dict)

base_url = 'http://www.basketball-reference.com/leagues/NBA_2017.html'
ratings_url = 'http://www.basketball-reference.com/leagues/NBA_2017_ratings.html'

def get_html(url):
    page =  urlopen(url).read()
    return page

html = get_html(base_url)
ratings_html = get_html(ratings_url)

def parse_team_ratings_per_game():
    ratings_html_parser = BeautifulSoup(ratings_html, 'html.parser')
    ratings_table = ratings_html_parser.find('table', {'class': 'stats_table'}).find('tbody')
    team_ratings = ratings_table.findAll('tr')

    for team in team_ratings:
        _parse_team_rating_to_json(team)



rating_to_index = {
    0: 'Team Name',
    7: 'Offensive Rating',
    8: 'Defensive Rating'
}

def _extract_team_name_from_link(team_link):
    return team_link.split('/')[2]

def _parse_team_rating_to_json(team_html):

    ratings_data = {}
    for index, column in enumerate(team_html.findAll('td')):
        if index in rating_to_index:
            label = rating_to_index[index]
            if index == 0:
                team_link = column.find('a', href=True)['href']
                value = _extract_team_name_from_link(team_link)
                team_value = value
            else:
                value = float(column.text)
            ratings_data[label] = value

    TEAM_RATINGS[team_value].update(ratings_data)


def parse_team_standings_per_game():
    standings_html = html
    standings_html_parser = BeautifulSoup(standings_html, 'html.parser')

    eastern_conference_standings = standings_html_parser.find('table', {'id': 'confs_standings_E'}).find('tbody')
    eastern_conference_teams = eastern_conference_standings.findAll('tr')
    for team in eastern_conference_teams:
        parse_team_standing(team)

    western_conference_standings = standings_html_parser.find('table', {'id': 'confs_standings_W'}).find('tbody')
    western_conference_teams = western_conference_standings.findAll('tr')
    for team in western_conference_teams:
        parse_team_standing(team)


standing_index_to_label = {
    4: 'scored',
    5: 'allowed'
}


def parse_team_pace(team_name):
    url = 'http://www.basketball-reference.com/teams/{0}/2017.html'.format(team_name)
    html = get_html(url)
    pace_index = html.find('Pace<')
    pace_html = html[pace_index:pace_index+40]

    try:
        pace = re.search('[0-9]{2,3}\.\d{1,2}', pace_html).group()
    except:
        print 'Team name: ', team_name
        import pdb; pdb.set_trace()
    return float(pace)


def parse_team_standing(team_html):

    team_info = {}
    team_name_href = team_html.find('th').find('a', href=True)['href']
    team_name = _extract_team_name_from_link(team_name_href)
    for index, column in enumerate(team_html.findAll('td')):
        if index in standing_index_to_label:
            label = standing_index_to_label[index]
            team_info[label] = float(column.text)

    TEAM_RATINGS[team_name].update(team_info)



if __name__ == '__main__':
    parse_team_ratings_per_game()
    parse_team_standings_per_game()

    print TEAM_RATINGS

    for team, value in TEAM_RATINGS.iteritems():
        pace = parse_team_pace(team)
        print 'parsing pace for team: {0} {1}'.format(team, pace)
        value['pace'] = pace


    with open('team_ratings.json', 'w') as team_ratings_json:
        team_data = TEAM_RATINGS.values()
        json.dump(team_data, team_ratings_json)
