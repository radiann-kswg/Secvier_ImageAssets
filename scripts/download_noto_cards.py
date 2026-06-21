#!/usr/bin/env python3
"""
Noto Sans Symbols2 playing card SVG downloader.
Run this from VS Code terminal (needs internet access):
    python scripts/download_noto_cards.py
"""
import urllib.request
import os
import time

DEST = os.path.join(os.path.dirname(__file__), "..", "src", "noto_cards")
os.makedirs(DEST, exist_ok=True)

FILES = [
    "PLAYING CARD JACK OF SPADES",
    "PLAYING CARD JACK OF HEARTS",
    "PLAYING CARD JACK OF DIAMONDS",
    "PLAYING CARD JACK OF CLUBS",
    "PLAYING CARD KNIGHT OF SPADES",
    "PLAYING CARD KNIGHT OF HEARTS",
    "PLAYING CARD KNIGHT OF DIAMONDS",
    "PLAYING CARD KNIGHT OF CLUBS",
    "PLAYING CARD QUEEN OF SPADES",
    "PLAYING CARD QUEEN OF HEARTS",
    "PLAYING CARD QUEEN OF DIAMONDS",
    "PLAYING CARD QUEEN OF CLUBS",
    "PLAYING CARD KING OF SPADES",
    "PLAYING CARD KING OF HEARTS",
    "PLAYING CARD KING OF DIAMONDS",
    "PLAYING CARD KING OF CLUBS",
    "PLAYING CARD BLACK JOKER",
    "PLAYING CARD RED JOKER",
]

BASE = "https://commons.wikimedia.org/wiki/Special:FilePath/"
HEADERS = {"User-Agent": "SecvierEmojiProject/1.0 (snine9801@gmail.com)"}

ok = 0
for name in FILES:
    fname = name + ".svg"
    url = BASE + fname.replace(" ", "_")
    dest_path = os.path.join(DEST, fname)
    try:
        req = urllib.request.Request(url, headers=HEADERS)
        with urllib.request.urlopen(req, timeout=20) as resp:
            data = resp.read()
        if len(data) < 100:
            print(f"  WARN  {fname}: too small ({len(data)} bytes)")
            continue
        with open(dest_path, "wb") as f:
            f.write(data)
        print(f"  OK    {fname} ({len(data):,} bytes)")
        ok += 1
    except Exception as e:
        print(f"  FAIL  {fname}: {e}")
    time.sleep(0.3)

print(f"\n{ok}/{len(FILES)} files downloaded to src/noto_cards/")
