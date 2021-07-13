# ett_parser.py

from typing import List, Optional, Iterator

import requests
import sys
import aiohttp
import asyncio
import urllib.parse
import pandas as pd

import nest_asyncio  # type: ignore


def get_or_create_eventloop():
    try:
        return asyncio.get_event_loop()
    except RuntimeError as ex:
        if "There is no current event loop in thread" in str(ex):
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            return asyncio.get_event_loop()


get_or_create_eventloop()
nest_asyncio.apply()


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
        print(f"Player with id{user_id} not found.")
        return [None]
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
        async with aiohttp.ClientSession(
            headers={"Connection": "keep-alive"}
        ) as session:
            tasks = []
            res = requests.get(
                __url(f"accounts/{user_id}/matches/?unranked={unranked_str}")
            ).json()
            last_page = res["links"]["last"]
            num_pages = int(last_page.split("page%5Bnumber%5D=")[1].split("&")[0])
            if num_pages == 1:
                matches = [res["data"]]
            else:
                for number in range(1, num_pages + 1):
                    url = __url(
                        f"accounts/{user_id}/matches/?page%5Bnumber%5D={number}&unranked={unranked_str}"
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


def get_matchup(user_id1, user_id2) -> Iterator:
    # TODO: webapi currently has a bug as it always returns 0 for home-score and away-score
    @__exception_handler
    def request_matchup(user_id1, user_id2):
        return requests.get(__url(f"matchup/{user_id1}/{user_id2}", legacy_api=True))

    r = request_matchup(user_id1, user_id2).json()
    res = r["data"]
    if len(res) == 0:
        return []

    rounds_data = r["included"]
    rounds_indexed = {}

    for r in rounds_data:
        rounds_indexed[r["id"]] = r["attributes"]

    for match_data in res:
        match = match_data["attributes"]
        match["home-elo-avg"] = match.pop("home-elo")
        match["away-elo-avg"] = match.pop("away-elo")
        match["winning-team"] = match.pop("winner")
        match["losing-team"] = 1 - match["winning-team"]

        # rounds data
        rounds = match_data["relationships"]["rounds"]["data"]
        num_rounds = len(rounds)
        match["rounds"] = []

        for i in range(num_rounds):
            current_round = rounds_indexed[
                match_data["relationships"]["rounds"]["data"][i]["id"]
            ]
            match["rounds"].append(current_round)
            match["rounds"][i]["winner"] = (
                0 if current_round["home-score"] > current_round["away-score"] else 1
            )

        # players data
        match["players"] = []
        home_away = ["home-team", "away-team"]
        for i in range(2):
            match["players"].append(match[home_away[i]][0])
            match["players"][i]["username"] = match[home_away[i]][0]["UserName"]
            match["players"][i]["elo"] = match[home_away[i]][0]["ELO"]
            match["players"][i]["rank"] = match[home_away[i]][0]["Rank"]
            match["players"][i]["wins"] = match[home_away[i]][0]["Wins"]
            match["players"][i]["losses"] = match[home_away[i]][0]["Losses"]
            match["players"][i]["last-online"] = match[home_away[i]][0]["LastOnline"]
            match["players"][i]["team"] = i

        match_data["attributes"] = match
        yield match_data


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


def get_leaderboard_official_tournament() -> List:
    @__exception_handler
    def request_leaderboard_official_tournament():
        return requests.get("http://lavadesignstudio.co.uk/eleven-rankings/")

    res = request_leaderboard_official_tournament()
    if res is None:
        print(f"Official Tournament Leaderboard Not Found.")
        return [None]
    else:
        return pd.read_html(res.text)


def user_search(username) -> List:
    username = urllib.parse.quote(username)
    async def request_user(session, url):
        async with session.get(url) as resp:
            user_page = await resp.json()
            return user_page["data"]

    async def get_user_async(username):
        async with aiohttp.ClientSession() as session:
            tasks = []
            res = requests.get(
                __url(f"accounts/search/{username}/", legacy_api=True)
            ).json()
            last_page = res["links"]["last"]
            num_pages = int(last_page.split("page%5Bnumber%5D=")[1].split("&")[0])
            if num_pages == 1:
                users = [res["data"]]
            else:
                for number in range(1, num_pages + 1):
                    url = __url(
                        f"accounts/search/{username}?page%5Bnumber%5D={number}",
                        legacy_api=True,
                    )
                    tasks.append(asyncio.ensure_future(request_user(session, url)))

                users = await asyncio.gather(*tasks)
            return users

    res = asyncio.run(get_user_async(username))
    all_pages = res[0]
    for page in res[1:]:
        all_pages.extend(page)

    return all_pages
