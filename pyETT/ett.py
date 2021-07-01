# pyETT.py

from typing import List

import pandas as pd
from pyETT import ett_parser


class Player:
    """
    A class to represent a Player.
    """

    HOME = 0
    AWAY = 1

    def __get_user(user_id):
        return ett_parser.get_user(user_id)

    def __new__(cls, user_id, player=None, legacy_api=False):
        if player is None:  # if no player is provided, try to get from the web api
            player = cls.__get_user(user_id)
            legacy_api = True
            if player is None:  # returns None if player not found in the web api
                return None
        instance = object.__new__(cls)
        instance.__init__(user_id, player, legacy_api)
        return instance

    def __init__(self, user_id, player=None, legacy_api=False):
        self.id = user_id
        if player is not None:
            self.name = player["user-name"] if legacy_api else player["username"]
            self.elo = player["elo"]
            self.rank = player["rank"]
            self.wins = player["wins"]
            self.losses = player["losses"]
            self.last_online = player["last-online"]
        self.friends = self.matches = self.elo_history = None

    def __str__(self):
        return self.name

    def get_friends(self) -> List["Player"]:
        """
        Return a player’s friends list
        """
        if self.friends is None:
            res = ett_parser.get_friends(self.id)
            if not res:
                self.friends = None
            else:
                self.friends = [
                    Player(user_id=v["id"], player=v["attributes"], legacy_api=True)
                    for v in res
                ]
        return self.friends

    def get_friends_dataframe(self) -> pd.DataFrame:
        """
        Return a player’s friends list in a dataframe
        """
        return pd.DataFrame([vars(u) for u in self.get_friends()]).dropna(
            how="all", axis="columns"
        )

    def get_matches(self, unranked=False) -> List["Match"]:
        """
        Return player’s matches.
        """
        if self.matches is None:
            res = ett_parser.get_matches(self.id, unranked)
            if not res:
                self.matches = None
            else:
                matches = [Match(match_id=v["id"], match=v["attributes"]) for v in res]
        return matches

    def get_matches_dataframe(self, unranked=False) -> pd.DataFrame:
        """
        Return player’s matches in a pandas dataframe.
        """
        return pd.DataFrame([vars(m) for m in self.get_matches(unranked)])

    def get_elo_history(self) -> pd.DataFrame:
        """
        Returns player’s elo score history.
        """
        if self.elo_history is None:
            res = ett_parser.get_elo_history(self.id)
            if not res:
                self.elo_history = None
            else:
                dt, elo = map(
                    list,
                    zip(
                        *[
                            (
                                v["attributes"]["created-at"],
                                v["attributes"]["current-elo"],
                            )
                            for v in res
                        ]
                    ),
                )

                self.elo_history = pd.DataFrame({"elo": elo}, index=dt)

        return self.elo_history


class Match:
    """
    A class to represent a Match.
    """

    class Round:
        """
        A class to represent a round of a Match.
        """

        def __init__(self, round_attributes):
            self.id = round_attributes["id"]
            self.round_number = round_attributes["round-number"]
            self.state = round_attributes["state"]
            self.away_score = round_attributes["away-score"]
            self.home_score = round_attributes["home-score"]
            self.winner = round_attributes["winner"]
            self.created_at = round_attributes["created-at"]

    def __init__(self, match_id, match):
        self.created_at = match["created-at"]
        self.id = match_id

        self.ranked = match["ranked"]
        self.number_of_rounds = match["number-of-rounds"]
        self.state = match["state"]
        self.winning_team = match["winning-team"]
        self.losing_team = match["losing-team"]
        self.home_score = match["home-score"]
        self.away_score = match["away-score"]

        home_player_index = 0 if match["players"][0]["team"] == Player.HOME else 1
        self.home_player = Player(
            match["players"][home_player_index]["id"],
            match["players"][home_player_index],
        )
        self.away_player = Player(
            match["players"][1 - home_player_index]["id"],
            match["players"][1 - home_player_index],
        )

        self.rounds = [self.Round(r) for r in match["rounds"]]

    def get_rounds_dataframe(rounds: List["round"]) -> pd.DataFrame:
        """
        Converts a list of rounds to a DataFrame
        """
        return pd.DataFrame([vars(r) for r in rounds])


class ETT:
    """
    A class to represent Eleven Table Tennis (ETT).
    """

    def __init__(self):
        self.leaderboard = None

    def user_search(self, username, perfect_match=False) -> List[Player]:
        """
        Returns a list of players whose name contains username, if perfect_match is False.
        Otherwise, it returns a list of players whose usernames is a perfect match with username.
        """
        res = ett_parser.user_search(username)

        if not res:
            users = None
        else:
            users = [
                Player(user_id=v["id"], player=v["attributes"], legacy_api=True)
                for v in res
                if (
                    not perfect_match
                    or (perfect_match and v["attributes"]["user-name"] == username)
                )
            ]

        return users

    def user_search_dataframe(self, username, perfect_match=False) -> pd.DataFrame:
        """
        Returns a list of players whose name contains username, if perfect_match is False.
        Otherwise, it returns a list of players whose usernames is a perfect match with username.
        """
        return pd.DataFrame(
            [vars(u) for u in self.user_search(username, perfect_match)]
        ).dropna(how="all", axis="columns")

    def get_leaderboard(self, num_players=10) -> List[Player]:
        """
        Returns a list of players from the leaderboard.
        """
        if self.leaderboard is None:
            res = ett_parser.get_leaderboard(num_players)
            if not res:
                self.leaderboard = None
            else:
                self.leaderboard = [
                    self.user_search(v["username"], perfect_match=True)[0] for v in res
                ]
        return self.leaderboard

    def get_leaderboard_dataframe(self, num_players=10) -> pd.DataFrame:
        """
        Returns a pandas dataframe with players from the leaderboard.
        """
        lb = pd.DataFrame([vars(u) for u in self.get_leaderboard(num_players)]).dropna(
            how="all", axis="columns"
        )
        # Overwriting rank as currently user API rank is lagged compared to the
        # rank in leaderboard API
        lb["rank"] = lb.index
        return lb
