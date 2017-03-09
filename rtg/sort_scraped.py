import click
import json


def_rating = lambda x: x['Defensive Rating']
off_rating = lambda x: x['Offensive Rating']
allowed = lambda x: x['allowed']
scored = lambda x: x['scored']


def load_raw_data():

    with open('team_ratings.json', 'r') as team_data:
        return json.load(team_data)


@click.command()
@click.option('--func', help='The sorting function to use')
@click.option('--descend/--ascend', help='The sort order', default=False)
def main(func, descend):
    raw_data = load_raw_data()

    if func == 'dr':
        key = def_rating
    elif func == 'or':
        key = off_rating
    elif func == 'allowed':
        key = allowed
    elif func == 'scored':
        key = scored

    sorted_raw_data = sorted(raw_data, key=key, reverse=descend)

    with open('ratings.json', 'w') as ratings:
        json.dump(sorted_raw_data, ratings)


if __name__ == '__main__':
    main()
