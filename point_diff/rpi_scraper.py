import click
from bs4 import BeautifulSoup
from urllib2 import urlopen
import json

base_url = 'http://www.espn.com/nba/stats/rpi'

INDEX_TO_LABEL = {
    1: 'Name',
    3: 'Wins',
    10: 'Expected W-L'
}


def get_rpi_html():
    return open('table.html').read()


def parse_rpi_data(rpi_html):
    rpi_html_parser = BeautifulSoup(rpi_html, 'html.parser')
    even_teams = rpi_html_parser.findAll('tr', attrs={'class': 'evenrow'})
    odd_teams = rpi_html_parser.findAll('tr', {'class': 'oddrow'})
    all_teams = even_teams + odd_teams

    all_team_data = []
    for team in all_teams:
        team_data = parse_team_data(team)
        all_team_data.append(team_data)
    print all_team_data

    return all_team_data


def parse_team_data(team_html):
    data = {}

    for i, d in enumerate(team_html.findAll('td')):
        if i in INDEX_TO_LABEL:
            label = INDEX_TO_LABEL[i]
            try:
                data[label] = int(d.text)
            except:
                data[label] = d.text

    data['Expected'] = int(data['Expected W-L'].split('-')[0])
    data['Diff'] = data['Wins'] - data['Expected']
    del data['Expected W-L']
    return data

data = parse_rpi_data(get_rpi_html())
data = sorted(data, key=lambda x: x['Diff'], reverse=True)


with open('nba_pt_diff.json', 'w') as e_pt_diff:
    json.dump(data, e_pt_diff)


