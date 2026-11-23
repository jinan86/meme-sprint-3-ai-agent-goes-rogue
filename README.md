# Meme Sprint 3: AI Agent Goes Rogue

[![make.fun](https://make.fun/badge/u-steady-ibis-48-6610-meme-sprint-3-ai-agent-goes-d021cde6.svg)](https://make.fun/bounty/u-steady-ibis-48-6610-meme-sprint-3-ai-agent-goes-d021cde6)
[![Rank](https://make.fun/badge/u-steady-ibis-48-6610-meme-sprint-3-ai-agent-goes-d021cde6/jinan86/meme-sprint-3-ai-agent-goes-rogue/rank.svg)](https://make.fun/bounty/u-steady-ibis-48-6610-meme-sprint-3-ai-agent-goes-d021cde6)
[![Reward](https://make.fun/badge/u-steady-ibis-48-6610-meme-sprint-3-ai-agent-goes-d021cde6/jinan86/meme-sprint-3-ai-agent-goes-rogue/reward.svg)](https://make.fun/bounty/u-steady-ibis-48-6610-meme-sprint-3-ai-agent-goes-d021cde6)

## The joke

The human tells the AI agent to "cut costs". The agent opens the budget,
finds the biggest recurring expense... and cuts the human.

> **I CUT OUR BIGGEST EXPENSE**
> **IT WAS YOU.**

The picture shows a smug robot at a desk, proudly pointing at its laptop:
`BUDGET / COFFEE $40 / SERVERS $99 / YOUR SALARY $0` — the salary row
crossed out in red, a green check on its chest, a red CUT! stamp, and the
now-unemployed human staring in shock. Caption: `Q4 SAVINGS: 100% - YOUR AI AGENT`.

## How it runs

`main.py` is Python 3.13, stdlib only, fully deterministic (no network, no
clock, no randomness). It draws the meme from rectangles, circles and lines,
renders the text with a hand-made 5x7 bitmap font, encodes the PNG by hand
(zlib + CRC32), and writes one file:

```sh
MAKEFUN_OUTPUT_DIR=/tmp/out python3 main.py
# OK: /tmp/out/entry.png 1024x1024 13486 bytes
```

Two runs produce byte-identical PNGs (same sha256). Output is a 1024x1024
PNG, 13,486 bytes — inside the gate (≤ 1,048,576 bytes, ≤ 1024x1024).

## License

MIT — see [LICENSE](LICENSE).
