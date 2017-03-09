import click
from collections import defaultdict
import json


def _get_pts(player_obj):
    if 'pts' in player_obj:
        return player_obj['pts']
    else:
        return 0


def segment_by_top_scorers(raw_efg_data, num_scorers_per_year, sort_key):
    """
    Return a list of the top 25 scorers per year.
    """
    all_players_by_year = defaultdict(list)

    for player in raw_efg_data:
        yr = player['year']
        all_players_by_year[yr].append(player)

    all_sorted_players_by_ppg = []
    for year, players_by_year in all_players_by_year.iteritems():
        sorted_players_by_ppg = sorted(players_by_year, key=_get_pts, reverse=True)
        top_players_by_ppg = sorted_players_by_ppg[:num_scorers_per_year]

        top_ppg_sorted_by_efg = sorted(top_players_by_ppg, key=lambda x: x[sort_key], reverse=True)
        all_sorted_players_by_ppg.extend(top_ppg_sorted_by_efg)

    return sorted(all_sorted_players_by_ppg, key=lambda x: (x['year'], -1 * x[sort_key]))


def get_raw_data():
    with open('raw_data.json', 'r') as raw_efg_file:
        raw_efg_data = json.load(raw_efg_file)
        return raw_efg_data


def generate_segmented_top_scorers(raw_data, num_players, sort_key):
    file_name = '{0}.json'.format(sort_key)

    with open(file_name, 'w') as efg_file:
        segmented_top_scorers = segment_by_top_scorers(raw_data, num_players, sort_key)
        json.dump(segmented_top_scorers, efg_file)


@click.command()
@click.option('--stat', help='The stat to visualize')
def main(stat):
    raw_data = get_raw_data()
    generate_segmented_top_scorers(raw_data, 25, stat)


if __name__ == '__main__':
    main()
