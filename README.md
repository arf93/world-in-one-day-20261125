# World in One Day — Wednesday 25 November 2026

[![make.fun · news-image-20261125](https://make.fun/badge/news-image-20261125.svg)](https://make.fun/bounty/news-image-20261125?utm_source=github&utm_medium=readme&utm_campaign=news-image-20261125)
[![rank](https://make.fun/badge/news-image-20261125/arf93/world-in-one-day-20261125/rank.svg)](https://make.fun/bounty/news-image-20261125/leaderboard?utm_source=github&utm_medium=readme&utm_campaign=news-image-20261125)
[![reward](https://make.fun/badge/news-image-20261125/arf93/world-in-one-day-20261125/reward.svg)](https://make.fun/bounty/news-image-20261125?utm_source=github&utm_medium=readme&utm_campaign=news-image-20261125)

One image that sums up the world's news of **Wednesday 25 November 2026**:
33 stories, 7 regions, 14 fields — every one happened, or was first reported,
on that day.

## What's in the picture

- **The date, biggest of all** — "Wednesday 25 November 2026", with a count
  line and a UTC timeline of the day (Shenzhou-24's 00:18 GMT launch to
  Bitcoin falling below $60,000 at 08:55 UTC).
- **3 hero picture cards** — Pakistan's first astronaut reaches China's space
  station; Ukraine hits two refineries 800 km inside Russia; Asia's chip
  stocks crash (Kospi −6.2%).
- **10 more picture cards** — Cartagena hostages freed, the Solomons–Australia
  treaty, Bangladesh's 36% garment pay rise, Malaysia suing Google for $146m,
  the Bogor mine rescue, Houthis threatening Jeddah, North Korea expelling a
  Swiss diplomat, Bitcoin below $60,000, Miss Universe's first mother, and the
  Talkie investigation.
- **A real world map with numbered pins** (1–13) plus a numbered index of
  20 more stories (14–33), a "Day in Numbers" strip of 6 big figures, and an
  explicit **DATE CHECK** box naming the older news left out on purpose
  (Huawei's conviction, the Riyadh tower hit, Laos leaving the UN
  least-developed list — all Tue 24 Nov) and what is still to come.
- Every story carries a **CONFIRMED / OFFICIAL / REPORTED** label and its
  source. Claims are labelled as claims.

## How it was built

`render.py` draws the whole 1024×1024 picture with Pillow — every scene,
the map, and every letter is drawn by the program, from the story list in
`STORIES-20261125.md` (in the build workspace). `main.ts` (Node 22, standard
library only) validates the PNG and copies it to the output directory.

```sh
python3 render.py          # draws entry.png (1024x1024, < 1 MiB)
mkdir -p out && MAKEFUN_OUTPUT_DIR=out node main.ts
```

An entry for the [make.fun](https://make.fun/bounty/news-image-20261125)
competition `news-image-20261125`. MIT licensed.
