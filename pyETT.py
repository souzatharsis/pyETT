# pyETT.py

from typing import List

import pandas as pd
import ett_parser


class Match:
    class Round:
        def __init__(self, round_attributes):
            self.id = round_attributes['id']
            self.round_number = round_attributes['round-number']
            self.state = round_attributes['state']
            self.away_score = round_attributes['away-score']
            self.home_score = round_attributes['home-score']
            self.winner = round_attributes['winner']
            self.created_at = round_attributes['created-at']

    def __init__(self, match_id, match):
        self.created_at = match['created-at']
        self.id = match_id

        self.ranked = match['ranked']
        self.number_of_rounds = match['number-of-rounds']
        self.state = match['state']
        self.winning_team = match['winning-team']
        self.losing_team = match['losing-team']
        self.home_score = match['home-score']
        self.away_score = match['away-score']

        home_player_index = 0 if match['players'][0]['team'] == 0 else 1
        self.home_player = Player(match['players'][home_player_index]["id"],
                                  match['players'][home_player_index])
        self.away_player = Player(match['players'][1 - home_player_index]["id"],
                                  match['players'][1 - home_player_index])

        self.rounds = [self.Round(r) for r in match['rounds']]

    def get_rounds_DataFrame(rounds) -> pd.DataFrame:
        return pd.DataFrame([vars(r) for r in rounds])


class Player:

    def __get_user(user_id):
        return ett_parser.get_user(user_id)

    def __init__(self, user_id, player=None, legacy_API=False):
        if player is None:
            player = self.__get_user(user_id)
            legacy_API = True
        self.id = user_id
        self.name = player['user-name'] if legacy_API else player['username']
        self.elo = player['elo']
        self.rank = player['rank']
        self.wins = player['wins']
        self.losses = player['losses']
        self.last_online = player['last-online']
        self.friends = self.matches = self.elo_history = None

    def __str__(self):
        return self.name

    def get_friends(self) -> List['Player']:
        if self.friends is None:
            res = ett_parser.get_friends(self.id)
            self.friends = [Player(user_id=v['id'], player=v["attributes"], legacy_API=True) for v in res]
        return self.friends

    def get_matches(self) -> List[Match]:
        if self.matches is None:
            res = ett_parser.get_matches(self.id)
            self.matches = [Match(match_id=v['id'], match=v["attributes"]) for v in res]
        return self.matches

    def get_matches_DataFrame(self) -> pd.DataFrame:
        return pd.DataFrame([vars(m) for m in self.get_matches()])

    def get_elo_history(self) -> pd.Series:
        if self.elo_history is None:
            res = ett_parser.get_elo_history(self.id)

            dt, elo = map(list, zip(*[(v['attributes']["created-at"], v['attributes']["current-elo"])
                                      for v in res]))

            self.elo_history = pd.Series(data=elo, index=dt)
        return self.elo_history


def user_search(username, perfect_match=False) -> List[Player]:
    res = ett_parser.user_search(username)

    users = [Player(user_id=v['id'],
                    player=v["attributes"],
                    legacy_API=True) for v in res if (not perfect_match
                                                      or (perfect_match
                                                          and v["attributes"]['user-name']
                                                          == username))]

    return users


def user_search_DataFrame(username) -> pd.DataFrame:
    return pd.DataFrame([vars(u) for u in user_search(username)]).dropna(how='all', axis='columns')


def get_leaderboard() -> List[Player]:
    res = ett_parser.get_leaderboard()
    users = [user_search(v["username"], perfect_match=True)[0] for v in res]
    return users


def get_leaderboard_DataFrame() -> pd.DataFrame:
    lb = pd.DataFrame([vars(u) for u in get_leaderboard()]).dropna(how='all', axis='columns')
    # Overwriting rank as currently user API rank is lagged compared to the rank in leaderboard API
    lb['rank'] = lb.index
    return lb
