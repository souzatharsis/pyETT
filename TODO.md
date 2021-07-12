## TODO

### Functions / params

- [ ] Add filter for match status

:heavy_check_mark: Find matches eligle for revertion

:heavy_check_mark: Cohort Analysis

:heavy_check_mark: Retrieve full user-matches history (parametrized) async

:heavy_check_mark: Retrieve full leaderboard (parametrized) async

:heavy_check_mark: Retrieve ranked and/or unranked matches (parametrized) async

### Documentation

- [ ] Add Changelog to docs

:heavy_check_mark: Add Docstrings

:heavy_check_mark: Add API official documentation

:heavy_check_mark: Add notebook demo

### Code cleaning, refactoring, testing

:heavy_check_mark: Split code into parser and ETT objects handling

:heavy_check_mark: Add unit tests

:heavy_check_mark: Handle request exceptions

:heavy_check_mark: Add enum for states variables


## Misc

- [ ] Add Elo analysis per player

https://colab.research.google.com/drive/1nIJCtDUWQFtFPjIRs_7_yox6uK3V3SUC?usp=sharing

`float K = (float)(32f * (2f - 1f / (Math.Pow(2.0, (double)(n - 1)))));`

Diffs compared to official Elo: different rounding, ignores manual elo change by mods, no 24 hour decay

- [ ] Predict match outcome based on match history: https://discord.com/channels/340715434099605515/581688710093996032/860572395009212456

:heavy_check_mark: Update ett-monthly app with new Tournament class

# Player Stats

1. overall record (win/loss)
2. overall winrate
3. highest Elo
4. ranking
5. winrate last 20 games
6. winrate last 50 games
7. winrate last 100 games
8. number of unique opponents
9. average daily matches (counting only days played days)
10. Date of first game
11. Number of days played
12. Number of days since first game

## Marathon day
1. Day with most matches
2. Highest number of matches in a day
3. Number of unique opponents in marathon day
4. Win/Loss
5. Net Elo change
6. Start of day Elo
7. End of day Elo

## Good/Bad day
1. Day with most Elo gain/loss
2. Highest Elo gain/loss in a day
3. Number of unique opponents in best/worst day day
4. Win/Loss
6. Start of day Elo
7. End of day Elo
