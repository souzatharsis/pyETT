# test_ett.py
import sys
sys.path.insert(1, '../')

from unittest import TestCase
from pyETT import ett


class ETTTesting(TestCase):

    def test_user_search(self):
        eleven = ett.ETT()
        player = eleven.user_search_dataframe('highlanderNJ', perfect_match=True)
        self.assertTrue(player.name[0] == 'highlanderNJ')

    def test_player(self):
        player = ett.Player(348353)

        self.assertTrue(player.name == 'highlanderNJ')

    def test_match(self):
        player = ett.Player(348353)
        matches = player.get_matches_dataframe().head()

        self.assertTrue(matches.shape[0] > 0)

    def test_match_rounds(self):
        player = ett.Player(348353)
        matches = player.get_matches_dataframe().head()
        rounds = ett.Match.get_rounds_dataframe(matches.loc[matches['id'] == '9530774',].rounds[0])

        self.assertTrue(rounds.shape[0] > 0)

    def test_friends(self):
        player = ett.Player(348353)
        friends = player.get_friends_dataframe()

        self.assertTrue(friends.shape[0] > 0)

    def test_elo_history(self):
        player = ett.Player(348353)
        player_elo = player.get_elo_history()

        self.assertTrue(player_elo.shape[0] > 0)
        self.assertTrue(player_elo.elo[0] >= 1500)

    def test_leaderboard(self):
        eleven = ett.ETT()
        leaderboard = eleven.get_leaderboard_dataframe()

        self.assertTrue(leaderboard.shape[0] > 0)
