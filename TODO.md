## TODO

### Modules

- [ ] Add player analytics module; bump minor version to v0.2

### Functions / params

- [ ] Add filter for match status

- [ ] Find matches eligle for revertion 

:heavy_check_mark: Retrieve full user-matches history (parametrized) async

:heavy_check_mark: Retrieve full leaderboard (parametrized) async

:heavy_check_mark: Retrieve ranked and/or unranked matches (parametrized) async

### Documentation

- [ ] Add Changelog

:heavy_check_mark: Add Docstrings

:heavy_check_mark: Add API official documentation

:heavy_check_mark: Add notebook demo

### Code cleaning, refactoring, testing

:heavy_check_mark: Split code into parser and ETT objects handling

:heavy_check_mark: Add unit tests

:heavy_check_mark: Handle request exceptions

:heavy_check_mark: Add enum for states variables


## Analytics Module

### Cohort Analysis

### Elo Analysis

https://colab.research.google.com/drive/1nIJCtDUWQFtFPjIRs_7_yox6uK3V3SUC?usp=sharing

`float K = (float)(32f * (2f - 1f / (Math.Pow(2.0, (double)(n - 1)))));`

Diffs compared to official Elo: different rounding, ignores manual elo change by mods, no 24 hour decay

### Player Analytics

https://jzyrobert.github.io/eleven-stats/


## Misc

- [ ] Predict match outcome based on match history: https://discord.com/channels/340715434099605515/581688710093996032/860572395009212456
