# ett_parser.py

from typing import List

import requests


def __url(path, legacy_API=False) -> str:
    return ('https://www.elevenvr.club/' if legacy_API else 'https://elevenvr.club/api/v1/') + path


def get_user(user_id) -> List:
    return requests.get(__url(f'accounts/{user_id}/', legacy_API=True)).json()['data']['attributes']


def get_friends(user_id) -> List:
    return requests.get(__url(f'accounts/{user_id}/', legacy_API=True) + "friends").json()['data']


def get_matches(user_id) -> List:
    return requests.get(__url(f'accounts/{user_id}/matches')).json()['data']


def get_elo_history(user_id) -> List:
    return requests.get(__url(f'accounts/{user_id}/', legacy_API=True) + 'elo-history').json()['data']


def get_leaderboard() -> List:
    return requests.get(__url(f'leaderboards/', legacy_API=True)).json()['scores']


def user_search(username) -> List:
    return requests.get(__url(f'accounts/search/{username}/', legacy_API=True)).json()['data']


