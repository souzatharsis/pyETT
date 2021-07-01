# ett_parser.py

from typing import List

import requests
import sys
import aiohttp
import asyncio


def __url(path, legacy_api=False) -> str:
    return (
               "https://www.elevenvr.club/" if legacy_api else "https://elevenvr.club/api/v1/"
           ) + path


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
        return requests.get(__url(f"accounts/{user_id}/", legacy_api=True))
    res = request_user(user_id)
    if res is None:
        print(f'Player with id{user_id} not found.')
        return None
    else:
        return res.json()["data"]["attributes"]


def get_friends(user_id) -> List:
    @__exception_handler
    def request_friends(user_id):
        return requests.get(__url(f"accounts/{user_id}/", legacy_api=True) + "friends")

    return request_friends(user_id).json()["data"]

def get_matches(user_id, unranked=False) -> List:
    async def request_matches(session, url):
        async with session.get(url) as resp:
            matches_page = await resp.json()
            return matches_page["data"]

    async def get_matches_async(user_id, unranked):
        unranked_str = "true" if unranked else "false"
        async with aiohttp.ClientSession() as session:
            tasks = []
            res = requests.get(__url(f"accounts/{user_id}/matches/?unranked={unranked_str}")).json()
            last_page = res["links"]["last"]
            num_pages = int(last_page.split('page%5Bnumber%5D=')[1].split('&')[0])
            if num_pages == 1:
                matches = [res["data"]]
            else:
                for number in range(1, num_pages + 1):
                    url = (
                        __url(f"accounts/{user_id}/matches/?page%5Bnumber%5D={number}&unranked={unranked_str}")
                    )
                    tasks.append(asyncio.ensure_future(request_matches(session, url)))

                matches = await asyncio.gather(*tasks)
            return matches

    res = asyncio.run(get_matches_async(user_id, unranked))
    all_pages = res[0]
    for page in res[1:]:
        all_pages.extend(page)

    return all_pages


def get_elo_history(user_id) -> List:
    @__exception_handler
    def request_elo_history(user_id):
        return requests.get(
            __url(f"accounts/{user_id}/", legacy_api=True) + "elo-history"
        )

    return request_elo_history(user_id).json()["data"]


def get_leaderboard(num_players=10):
    async def request_leaderboard(session, url):
        async with session.get(url) as resp:
            lb_page = await resp.json()
            return lb_page["scores"]

    async def get_leaderboard_async(num_players):
        async with aiohttp.ClientSession() as session:
            tasks = []
            for number in range(0, num_players // 10 + 1):
                url = (
                        __url(f"leaderboards/", legacy_api=True)
                        + "?start="
                        + str(number * 10)
                )
                tasks.append(asyncio.ensure_future(request_leaderboard(session, url)))

            lb = await asyncio.gather(*tasks)
            return lb

    res = asyncio.run(get_leaderboard_async(num_players))
    all_pages = res[0]
    for page in res[1:]:
        all_pages.extend(page)

    return all_pages[:num_players]


def user_search(username) -> List:
    async def request_user(session, url):
        async with session.get(url) as resp:
            user_page = await resp.json()
            return user_page["data"]

    async def get_user_async(username):
        async with aiohttp.ClientSession() as session:
            tasks = []
            res = requests.get(__url(f"accounts/search/{username}/", legacy_api=True)).json()
            last_page = res["links"]["last"]
            num_pages = int(last_page.split('page%5Bnumber%5D=')[1].split('&')[0])
            if num_pages == 1:
                users = [res["data"]]
            else:
                for number in range(1, num_pages + 1):
                    url = (
                        __url(f"accounts/search/{username}?page%5Bnumber%5D={number}", legacy_api=True)
                    )
                    tasks.append(asyncio.ensure_future(request_user(session, url)))

                users = await asyncio.gather(*tasks)
            return users

    res = asyncio.run(get_user_async(username))
    all_pages = res[0]
    for page in res[1:]:
        all_pages.extend(page)

    return all_pages
