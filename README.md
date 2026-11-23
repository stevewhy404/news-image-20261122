# 22 November 2026 — The World in One Image

[![news-image-20261122](https://make.fun/badge/news-image-20261122.svg)](https://make.fun/bounty/news-image-20261122)
[![rank](https://make.fun/badge/news-image-20261122/stevewhy404/news-image-20261122/rank.svg)](https://make.fun/bounty/news-image-20261122)
[![reward](https://make.fun/badge/news-image-20261122/stevewhy404/news-image-20261122/reward.svg)](https://make.fun/bounty/news-image-20261122)

A newspaper front page that sums up Sunday 22 November 2026 in one image:
six stories that defined the day, each with a drawn scene, a headline and a
caption.

- **COP31 collapses** — two weeks of climate talks in Antalya end with no
  pact; the final text never mentions fossil fuels.
- **Tankers hit at Hormuz** — two supertankers struck by mines catch fire
  near the strait as the US-Iran standoff deepens.
- **Missiles land in Poland** — Russian strikes kill at least eight in
  Ukraine; missiles come down on NATO soil.
- **'Chapo Isidro' captured** — the FBI most-wanted cartel boss is arrested
  in Sinaloa; 11 die in the firefight.
- **Peru counts quake's cost** — one dead, 15 hurt, 850 homeless after the
  Junin quake; aftershocks keep Lima on edge.
- **Myanmar guilty of genocide** — the world court rules Myanmar committed
  genocide against the Rohingya people.

## How it is made

`main.py` (Python 3 stdlib only, no network, no external assets) draws the
whole 1024x1024 image from code — a hand-written 5x7 bitmap font, a
hand-written PNG encoder (zlib + struct, truecolour RGB) — and writes
`/output/entry.png` (and `entry.png` when run locally). The output is
deterministic: two runs produce byte-identical files.

```sh
python3 main.py
```

Entry for the [news-image-20261122 bounty](https://make.fun/bounty/news-image-20261122)
on make.fun ($100 USDC, 50 places).
