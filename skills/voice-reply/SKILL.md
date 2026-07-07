---
name: voice-reply
description: Reply to a channel message with a synthesized voice note instead of text. Use when the user explicitly asks to hear a voice reply.
---

# Voice Reply

Turn your text answer into a voice note with speak.py (edge-tts), then send it
through the channel's reply tool as an audio attachment. The mirror image of the
voice-transcribe skill.

## Prerequisite (one time)

`./setup.sh` from the repo root installs edge-tts into `.venv` along with the
transcription dependencies.

## Steps

1. Write your reply as plain text.
2. Synthesize it to an mp3:

   ```bash
   /ABSOLUTE/PATH/TO/cc-telegram-voice/.venv/bin/python \
     /ABSOLUTE/PATH/TO/cc-telegram-voice/speak.py \
     "<your reply text>" --voice zh-CN-YunxiNeural --out reply.mp3
   ```

   Replace the path with wherever you cloned this repo. Swap `--voice` for any
   language or voice (`speak.py --list-voices`). Tune pace and tone with `--rate`
   and `--pitch`, e.g. `--rate=-11% --pitch=-2Hz`.

3. Send the mp3 through the channel's reply tool as a file attachment. For the
   Telegram plugin that is `reply` with `files: ["<path>/reply.mp3"]`.

## When to use voice vs text

Default to text: it is glanceable on a watch, rereadable, and searchable, and
long or structured answers read better. Reach for voice only when the user
explicitly asks for it. Sending a voice note does not, on its own, mean the user
wants voice back unless they say so.

## Privacy

speak.py sends the text to Microsoft's endpoint to synthesize it (unlike the
fully local transcribe.py). Keep anything private in text.
