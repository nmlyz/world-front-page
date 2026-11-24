# world-front-page

[![make.fun · news-image-20261124](https://make.fun/badge/news-image-20261124.svg)](https://make.fun/bounty/news-image-20261124?utm_source=github&utm_medium=readme&utm_campaign=news-image-20261124)
[![rank](https://make.fun/badge/news-image-20261124/nmlyz/world-front-page/rank.svg)](https://make.fun/bounty/news-image-20261124/leaderboard?utm_source=github&utm_medium=readme&utm_campaign=news-image-20261124)
[![reward](https://make.fun/badge/news-image-20261124/nmlyz/world-front-page/reward.svg)](https://make.fun/bounty/news-image-20261124?utm_source=github&utm_medium=readme&utm_campaign=news-image-20261124)

A single-file Python program that draws a newspaper front page summing up the world news of Tuesday 24 November 2026 — a Ukrainian sea drone sinking a Russian corvette in Benghazi, three more ships hit in the Strait of Hormuz, new EU sanctions aimed at 60 Russian banks, Democrats taking 258 House seats, aid workers killed in Gaza, drone strikes on Khartoum, students flooding the streets of Europe, and Seoul naming new top diplomats — as one 1024x1024 PNG, drawn entirely with code (a hand-made bitmap font, no external assets) using only the Python standard library.

The page follows a broadsheet hierarchy: a masthead with a numbers strip (258 seats, 60 banks, 330 votes, 3 ships, 100+ cities), a double-size lead story with a large illustration panel, and secondary stories in varied box sizes, each with a region kicker, a dateline, and factual lines with hard numbers.

## Run it

```sh
mkdir -p out && MAKEFUN_OUTPUT_DIR=out python3 main.py
```

The program writes `entry.png` to the output directory. It uses no network and is fully deterministic: every run produces the same bytes.
