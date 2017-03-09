from bs4 import BeautifulSoup
from urllib2 import urlopen
import json


INDEX_TO_STAT_MAP = {
    0: 'name',
    9: 'fg',
    16: 'efg',
    10: '3ptm',
    11: '3pta',
    12: '3fg',
    28: 'pts'
}


player_page_base_url = 'http://www.basketball-reference.com/leagues/NBA_{year}_per_game.html'


def get_player_page_html(year):

    player_page_url = player_page_base_url.format(year=year)
    page = urlopen(player_page_url).read()
    return page


def parse_player_page(year_html_data, year):
    """
    Parse a season stat's page into a list of player dictionaries.
    """
    player_page_html_parser = BeautifulSoup(year_html_data, 'html.parser')
    stats_table = player_page_html_parser.find('table', {'class': 'stats_table'}).find('tbody')
    players = stats_table.findAll('tr', {'class': 'full_table'})

    player_info = []
    for player in players:
        player_info.append(_parse_player_row_to_dict(player, year))

    return player_info


def _parse_player_row_to_dict(player_row, year):
    """
    Parse a player table row into a dictionary of relevant stats.
    """
    player_data = {'year': year}
    for index, column in enumerate(player_row.findAll('td')):
        if index in INDEX_TO_STAT_MAP:
            stat_name = INDEX_TO_STAT_MAP[index]
            try:
                stat_value = float(column.text)
            except:
                stat_value = column.text
            player_data[stat_name] = stat_value

    return player_data


def write_to_json(player_data):

    with open('raw_data.json', 'w') as player_json:
        json.dump(player_data, player_json)


if __name__ == '__main__':

    all_years = range(2003, 2011)
    all_years.append(2017)

    player_data_for_all_years = []
    for yr in all_years:
        player_page_html = get_player_page_html(yr)
        player_data_for_all_years.extend(parse_player_page(player_page_html, yr))

    write_to_json(player_data_for_all_years)
