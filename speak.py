#!/usr/bin/env python3
"""Text-to-speech for Claude Code channels, free and no API key.

The flip side of transcribe.py. transcribe.py turns an incoming voice note into
text; speak.py turns Claude's text reply back into a voice note, so a channel
can be two-way voice. It uses edge-tts (Microsoft Edge's online neural voices),
which are free and need no key.

PRIVACY: unlike transcribe.py, which is fully local, edge-tts sends the text to
Microsoft's endpoint to synthesize it. Do not use it for text you must keep
private.

Usage:
  python speak.py "你好，很高兴见到你" --voice zh-CN-YunxiNeural --out reply.mp3
  echo "hello there" | python speak.py - --voice en-US-GuyNeural --out reply.mp3
  python speak.py --list-voices | grep zh-CN

--rate and --pitch tune pace and tone, e.g. --rate=-11% --pitch=-2Hz. A flatter,
calmer cadence comes mostly from writing the text with few internal commas
(pauses fall on full stops), not just from these flags.
"""

import argparse
import asyncio
import sys


async def synth(text, voice, rate, pitch, out):
    import edge_tts
    kwargs = {}
    if rate:
        kwargs["rate"] = rate
    if pitch:
        kwargs["pitch"] = pitch
    await edge_tts.Communicate(text, voice, **kwargs).save(out)


async def show_voices():
    import edge_tts
    for v in await edge_tts.list_voices():
        print(f"{v['ShortName']:34} {v['Gender']:8} {v.get('FriendlyName', '')}")


def main():
    p = argparse.ArgumentParser(description="Text to speech via edge-tts (online, no key).")
    p.add_argument("text", nargs="?", help="text to speak, or '-' to read stdin")
    p.add_argument("--voice", default="zh-CN-YunxiNeural", help="edge-tts voice short name")
    p.add_argument("--rate", default="", help="pace, e.g. -11% (slower) or +10% (faster)")
    p.add_argument("--pitch", default="", help="tone, e.g. -2Hz")
    p.add_argument("--out", default="reply.mp3", help="output mp3 path")
    p.add_argument("--list-voices", action="store_true", help="print all voices and exit")
    args = p.parse_args()

    if args.list_voices:
        asyncio.run(show_voices())
        return

    text = sys.stdin.read() if args.text == "-" else args.text
    if not text or not text.strip():
        p.error("no text given (pass a string, or '-' to read stdin)")

    asyncio.run(synth(text, args.voice, args.rate, args.pitch, args.out))
    print(args.out)


if __name__ == "__main__":
    main()
