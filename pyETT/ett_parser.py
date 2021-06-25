# ett_parser.py

from typing import List

import requests
import sys


def __url(path, legacy_api=False) -> str:
    return (
               'https://www.elevenvr.club/' if legacy_api else 'https://elevenvr.club/api/v1/') + path


def __exception_handler(func):
    def inner_function(*args, **kwargs):
        try:
            response = func(*args, **kwargs)
            response.raise_for_status()
            # Code here will only run if the request is successful
            return response
        except requests.exceptions.HTTPError as errh:
            print(errh)
        except requests.exceptions.ConnectionError as errc:
            print(errc)
        except requests.exceptions.Timeout as errt:
            print(errt)
        except requests.exceptions.RequestException as err:
            print(err)

    return inner_function


def get_user(user_id) -> List:
    @__exception_handler
    def request_user(user_id):
        return requests.get(
            __url(
                f'accounts/{user_id}/',
                legacy_api=True))

    return request_user(user_id).json()['data']['attributes']


def get_friends(user_id) -> List:
    @__exception_handler
    def request_friends(user_id):
        return requests.get(
            __url(
                f'accounts/{user_id}/',
                legacy_api=True) + "friends")

    return request_friends(user_id).json()['data']


def get_matches(user_id) -> List:
    @__exception_handler
    def request_matches(user_id):
        return requests.get(__url(f'accounts/{user_id}/matches'))

    return request_matches(user_id).json()['data']


def get_elo_history(user_id) -> List:
    @__exception_handler
    def request_elo_history(user_id):
        return requests.get(
            __url(
                f'accounts/{user_id}/',
                legacy_api=True) + 'elo-history')

    return request_elo_history(user_id).json()['data']


def get_leaderboard() -> List:
    @__exception_handler
    def request_leaderboard():
        return requests.get(
            __url(
                f'leaderboards/',
                legacy_api=True))

    return request_leaderboard().json()['scores']


def user_search(username) -> List:
    @__exception_handler
    def request_leaderboard(username):
        return requests.get(
            __url(
                f'accounts/search/{username}/',
                legacy_api=True))

    return request_leaderboard(username).json()['data']
