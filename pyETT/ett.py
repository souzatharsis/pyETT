# pyETT.py

from pyETT import ett_parser
from typing import List, Optional, Union
from functools import reduce
from itertools import combinations
import pandas as pd
import numpy as np

pd.options.mode.chained_assignment = None


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
        self.id = np.int64(user_id)
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

    def __hash__(self):
        return int(self.id)

    def __lt__(self, other):
        return self.elo < other.elo

    def __eq__(self, other):
        return np.int64(self.id) == np.int64(other.id)

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

    def get_matches(self, unranked: bool = False) -> List["Match"]:
        """
        Return player’s matches.
        """
        if self.matches is None:
            res = ett_parser.get_matches(self.id, unranked)
            if not res:
                matches = []
            else:
                matches = [Match(match_id=v["id"], match=v["attributes"]) for v in res]
        else:
            matches = self.matches
        return matches

    def get_matches_dataframe(self, unranked: bool = False) -> pd.DataFrame:
        """
        Return player’s matches in a pandas dataframe.
        """
        return pd.DataFrame(
            [vars(m) for m in self.get_matches(unranked) if m is not None]
        )

    def get_matches_revertible(self) -> List[np.int64]:
        """Returns player's lost matches that are eligible to be reverted/cancelled.
        If you have an incomplete match because of connection issues or because your opponent left in the middle of the play,
        you can request an Eleven Moderator (Discord) to revert/cancel the match and hence update your Elo rating.

        Returns:
            List[np.int64]: List of matches ids that are eligible to be reverted/cancelled.
        """
        m = self.get_matches_dataframe()
        m["number_of_played_rounds"] = m["home_score"] + m["away_score"]
        m["winner"] = m["home_player"]
        m.loc[m["winning_team"] == 1, "winner"] = m.loc[
            m["winning_team"] == 1, "away_player"
        ]
        m_incomplete = m.loc[
            ((m["ranked"]) & (m["winner"] != self))
            & ((m["state"] != 1) | (m["number_of_played_rounds"] < 2)),
        ]

        return list(m_incomplete.id.values)

    def print_matches_revertible(self):
        """Pretty print player's lost matches that are eligible to be reverted/cancelled.
        If you have an incomplete match because of connection issues or because your opponent left in the middle of the play,
        you can request an Eleven Moderator (Discord) to revert/cancel the match and hence update your Elo rating
        """
        m_incomplete_id_values = self.get_matches_revertible()

        [print_match(m) for m in self.get_matches() if m.id in m_incomplete_id_values]

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
            self.id = np.int64(round_attributes["id"])
            self.round_number = round_attributes["round-number"]
            self.state = round_attributes["state"]
            self.away_score = round_attributes["away-score"]
            self.home_score = round_attributes["home-score"]
            self.winner = round_attributes["winner"]
            self.created_at = round_attributes["created-at"]

    def __init__(self, match_id, match):
        self.created_at = match["created-at"]
        self.id = np.int64(match_id)

        self.ranked = match["ranked"]
        self.number_of_rounds = match["number-of-rounds"]
        self.state = match["state"]
        self.winning_team = match["winning-team"]
        self.losing_team = match["losing-team"]
        self.home_score = match["home-score"]
        self.away_score = match["away-score"]
        self.elo_change = match["elo-change"]

        home_player_index = 0 if match["players"][0]["team"] == Player.HOME else 1
        self.home_player = Player(
            match["players"][home_player_index]["id"],
            match["players"][home_player_index],
        )
        self.away_player = Player(
            match["players"][1 - home_player_index]["id"],
            match["players"][1 - home_player_index],
        )

        self.rounds = [self.Round(r) for r in match["rounds"]][::-1]

    def print(self):
        print_match(self)

    # Keeping inside Match for organizational / readability purposes even though it's a static method.
    def get_rounds_dataframe(rounds: List["Round"]) -> pd.DataFrame:  # type: ignore
        """Converts a list of rounds to a DataFrame
        Args:
            rounds (List["Round"]): List of rounds.

        Returns:
            pd.DataFrame: Dataframe with rounds, one per row.
        """
        # I reverse the list because rounds come in reverse order from the web api for some reason
        return pd.DataFrame([vars(r) for r in rounds if r is not None])


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

        return (
            []
            if not res
            else [
                Player(user_id=v["id"], player=v["attributes"], legacy_api=True)
                for v in res
                if (
                    v is not None
                    and (
                        not perfect_match
                        or (perfect_match and v["attributes"]["user-name"] == username)
                    )
                )
            ]
        )

    def user_search_dataframe(
        self, username: str, perfect_match: bool = False
    ) -> pd.DataFrame:
        """
        Returns a list of players whose name contains username, if perfect_match is False.
        Otherwise, it returns a list of players whose usernames is a perfect match with username.
        """
        return pd.DataFrame(
            [
                vars(u)
                for u in self.user_search(username, perfect_match)
                if u is not None
            ]
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

    def get_leaderboard_dataframe(self, num_players: int = 10) -> pd.DataFrame:
        """
        Returns a pandas dataframe with players from the leaderboard.
        """
        lb = pd.DataFrame(
            [vars(u) for u in self.get_leaderboard(num_players) if u is not None]
        ).dropna(how="all", axis="columns")
        # Overwriting rank as currently user API rank is lagged compared to the
        # rank in leaderboard API
        lb["rank"] = lb.index
        return lb


class Cohort:
    """
    A Class to represent a cohort of players
    """

    def __init__(self, players):
        self.players = list(filter(None, players))
        self.size = len(self.players)
        self.matches = None

    def players_dataframe(self):
        """
        Returns cohort's players in a dataframe
        """

        return pd.DataFrame([vars(u) for u in self.players if u is not None]).dropna(
            how="all", axis="columns"
        )

    def get_elo_history(self):
        """
        Returns Elo history of the players in the cohort
        """
        cohort_elo = [
            p.get_elo_history().rename(columns={"elo": p.name})
            for p in self.players
            if p.get_elo_history() is not None
        ]

        return reduce(
            lambda df1, df2: pd.merge(
                df1, df2, how="outer", left_index=True, right_index=True
            ),
            cohort_elo,
        ).ffill(axis=0)

    def get_matches(self, unranked: bool = False) -> List["Match"]:
        """
        Returns matches among players in the cohort
        """

        def get_matchup(matchup):
            res = ett_parser.get_matchup(matchup[0].id, matchup[1].id)
            if not res:
                matches = []
            else:
                matches = [Match(match_id=v["id"], match=v["attributes"]) for v in res]
            return matches

        if self.matches is None:
            players_matchup = combinations(self.players, 2)
            players_matches = []
            [
                players_matches.extend(get_matchup(matchup))  # type: ignore
                for matchup in players_matchup
            ]
            self.matches = players_matches

        return self.matches

    def get_matches_dataframe(self, unranked: bool = False) -> pd.DataFrame:
        """
        Returns a dataframe containing all matches of the players in the cohort.
        """
        return pd.DataFrame(
            [vars(m) for m in self.get_matches(unranked) if m is not None]
        )

    def describe(self) -> pd.DataFrame:
        """
        Returns a dataframe with descriptive statistics of the players in the cohort considering only matches among themselves, such as win, losses and win rate.
        Additional player specific attributes are added to the dataframe, such as name, elo and rank.

        Returns:
            pd.DataFrame: Players matchup stats in the cohort.
        """
        matches = self.get_matches_dataframe(self.players)

        def matches_stats(matches, ranked):
            ranked_label = ""
            if ranked:
                ranked_label += "_ranked"
                matches = matches.loc[
                    matches["ranked"],
                ]

            matches["winner"] = matches["home_player"]
            matches.loc[matches["winning_team"] == 1, "winner"] = matches.loc[
                matches["winning_team"] == 1, "away_player"
            ]

            wins = matches["winner"].value_counts()
            num_matches = (
                matches["home_player"].value_counts()
                + matches["away_player"].value_counts()
            )
            losses = num_matches - wins
            win_rate = (wins / num_matches) * 100

            frame = {
                ("num_matches" + ranked_label): num_matches,
                ("wins" + ranked_label): wins,
                ("losses" + ranked_label): losses,
                ("win_rate" + ranked_label): win_rate,
            }
            return pd.DataFrame(frame).reset_index()

        ranked_stats = matches_stats(matches, ranked=True)
        all_stats = matches_stats(matches, ranked=False)
        cohort_stats = (
            ranked_stats.merge(all_stats)
            .round(0)
            .sort_values(by=["win_rate_ranked"], ascending=False)
        )
        cohort_stats["id"] = [p.id for p in cohort_stats["index"]]
        cohort_players = self.players_dataframe()[["id", "elo", "rank"]]
        # cohort_players["id"] = cohort_players["id"].astype(np.int64)

        return cohort_stats.merge(
            cohort_players,
            left_on="id",
            right_on="id",
        ).drop(columns=["id"])


class Tournament:
    """
    A Class to handle ETT official tournaments
    """

    def __init__(self, players):
        self.players = list(filter(None, players))
        self.size = len(self.players)

    def qualify(self, elo_min: float, start: str, end: str) -> pd.DataFrame:
        """Implements logic to enter or qualify to ETT's official monthly tournament.
        Players with an Elo rating exceeding ``elo_min`` at any point
        between ``start`` and ``end`` date have direct entry to the tournament.
        Otherwise, they can enter a Qualifying Tournament to try and qualify.
        This method returns a dataframe indicating which players have direct entry
        or can qualify.

        Args:
            elo_min (float): Elo threshold to have direct entry to the Tournament.
            start (str): Start date (YYYY-MM-DD)
            end (str): End date (YYYY-MM-DD)

        Returns:
            pd.DataFrame: Data frame of players with the following information:
                - mean: Player's mean Elo between ``start`` and ``end``
                - min: Player's min Elo between ``start`` and `end``
                - max: Player's max Elo between ``start`` and `end``
                - direct_entry: Boolean indicating whether player have direct entry to the Tournament
                - can_qualify: Boolean indicating whether player can enter Qualifying Tournament
                - id: Player's id
                - name: Player's username
        """

        p_with_elo = [p for p in self.players if p.get_elo_history() is not None]
        ids = [p.id for p in p_with_elo]

        # Players with elo history
        players_elo = [
            p.get_elo_history().rename(columns={"elo": p.name}) for p in p_with_elo
        ]

        group_elo_df = reduce(
            lambda df1, df2: pd.merge(
                df1, df2, how="outer", left_index=True, right_index=True
            ),
            players_elo,
        ).ffill(axis=0)

        monthly_stats = (
            group_elo_df.loc[
                (group_elo_df.index >= start) & (group_elo_df.index <= end)
            ]
            .describe()
            .filter(like="m", axis=0)
            .transpose()
        )
        monthly_stats["direct_entry"] = monthly_stats["max"] > elo_min
        monthly_stats["can_qualify"] = monthly_stats["min"] <= elo_min
        monthly_stats["id"] = [p.id for p in p_with_elo]
        monthly_stats["name"] = [p.name for p in p_with_elo]

        # Players with no elo history
        p_without_elo = [p for p in self.players if p.get_elo_history() is None]

        ids_without_elo = [p.id for p in p_without_elo]
        n = len(ids_without_elo)
        d = {
            "mean": [1500] * n,
            "min": [1500] * n,
            "max": [1500] * n,
            "direct_entry": [False] * n,
            "can_qualify": [True] * n,
            "id": ids_without_elo,
            "name": [p.name for p in p_without_elo],
        }

        return pd.concat([monthly_stats, pd.DataFrame(data=d)], ignore_index=True)


def official_tournament_leaderboard_dataframe() -> pd.DataFrame:
    """
    Returns a pandas dataframe with the leaderboard of the Eleven official tournaments
    available at http://lavadesignstudio.co.uk/eleven-rankings/.
    """
    return ett_parser.get_leaderboard_official_tournament()[0]


def print_match(match: Match):
    """Pretty print a match with rounds.

    Args:
        match (Match): A match.
    """    
    print(f"Match #{match.id} : {match.created_at}\n")
    home_elo_sign = (-1) ** match.winning_team
    df = pd.DataFrame(
        {
            "USERNAME": [match.home_player.name, match.away_player.name],
            "ELO +-": [
                home_elo_sign * match.elo_change,
                -home_elo_sign * match.elo_change,
            ],
            "MATCH SCORE": [match.home_score, match.away_score],
        }
    )
    df_rounds = Match.get_rounds_dataframe(match.rounds)
    for index2, row2 in df_rounds.iterrows():
        round_index = int(index2) + 1
        df[f"ROUND {round_index}"] = [row2["home_score"], row2["away_score"]]
    print(df)
    print("\n")
