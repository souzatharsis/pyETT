# test_ett.py
import sys

sys.path.insert(1, "../")

from unittest import TestCase
from pyETT import ett


class ETTTesting(TestCase):
    def test_user_search(self):
        eleven = ett.ETT()
        player = eleven.user_search_dataframe("highlanderNJ", perfect_match=True)
        self.assertTrue(player.name[0] == "highlanderNJ")

    def test_leaderboard(self):
        eleven = ett.ETT()
        leaderboard = eleven.get_leaderboard_dataframe()

        self.assertTrue(leaderboard.shape[0] > 0)


class PlayerTesting(TestCase):
    def test_player(self):
        player = ett.Player(348353)

        self.assertTrue(player.name == "highlanderNJ")

    def test_friends(self):
        player = ett.Player(348353)
        friends = player.get_friends_dataframe()

        self.assertTrue(friends.shape[0] > 0)

    def test_elo_history(self):
        player = ett.Player(348353)
        player_elo = player.get_elo_history()

        self.assertTrue(player_elo.shape[0] > 0)
        self.assertTrue(player_elo.elo[0] >= 1500)


class MatchTesting(TestCase):
    def test_match(self):
        player = ett.Player(348353)
        matches = player.get_matches_dataframe().head()

        self.assertTrue(matches.shape[0] > 0)

    def test_match_ranked(self):
        player = ett.Player(348353)
        matches = player.get_matches_dataframe(unranked=False)

        self.assertTrue(matches.ranked.any())

    def test_match_unranked(self):
        player = ett.Player(348353)
        matches = player.get_matches_dataframe(unranked=True)

        self.assertTrue(not (matches.ranked).all())

    def test_match_rounds(self):
        player = ett.Player(348353)
        matches = player.get_matches_dataframe()
        rounds = ett.Match.get_rounds_dataframe(
            rounds=matches.loc[
                matches["id"] == 9866478,
            ].rounds.values[0]
        )

        self.assertTrue(rounds.shape[0] > 0)


class CohortTesting(TestCase):
    def test_get_matches_dataframe(self):
        p1 = ett.Player(357217)
        p2 = ett.Player(348353)
        c = ett.Cohort([p1, p2])
        self.assertTrue(c.get_matches_dataframe().head().shape[0] > 0)

    def test_describe(self):
        p1 = ett.Player(357217)
        p2 = ett.Player(348353)
        c = ett.Cohort([p1, p2])
        self.assertTrue(c.describe().shape[0] > 0)


class TournamentTesting(TestCase):
    def test_get_official_tournament_leaderboard_dataframe(self):
        leaderboard = ett.official_tournament_leaderboard_dataframe()

        self.assertTrue(leaderboard.shape[0] > 0)