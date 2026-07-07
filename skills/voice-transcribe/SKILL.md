---
name: voice-transcribe
description: Transcribe an incoming Telegram (or other) voice message to text, fully offline. Use whenever a channel message arrives with an audio attachment and you need to know what was said.
---

# Voice Transcribe

Turn a voice message into text on the local machine, without sending audio to
any cloud service. Backed by PyAV (decode) plus whisper.cpp (recognition).

## When to use

A Telegram voice note arrives as a channel block whose meta carries an
`attachment_file_id` and an audio mime type, for example:

```
<channel source="telegram" chat_id="..." attachment_file_id="AwAC..." attachment_mime="audio/ogg">
(voice message)
</channel>
```

You cannot read a voice note directly. Transcribe it first, then respond to the
text as usual.

## Prerequisite (one time)

From the repo root, run `./setup.sh`. It builds whisper.cpp, downloads a model,
and creates a `.venv` with PyAV. Nothing leaves the machine.

## Steps

1. **Download the audio.** Call the Telegram plugin's `download_attachment`
   with the `attachment_file_id` from the channel meta. It returns a local path
   to a `.oga` file.

2. **Transcribe.** Run the transcriber with the repo's virtualenv python:

   ```bash
   /ABSOLUTE/PATH/TO/cc-telegram-voice/.venv/bin/python \
     /ABSOLUTE/PATH/TO/cc-telegram-voice/transcribe.py \
     "<downloaded .oga path>" --lang zh
   ```

   Replace `/ABSOLUTE/PATH/TO/cc-telegram-voice` with wherever you cloned this
   repo. Use `--lang zh` for Chinese, `--lang en` for English, or `--lang auto`
   to let whisper detect. The transcript is printed to stdout.

3. **Act on the transcript.** Treat the printed text as if the user had typed
   it, and reply through the normal channel reply tool.

## Notes

- Telegram voice notes are ogg/opus; PyAV decodes them without a system ffmpeg.
- WeChat voice messages use the SILK codec, which FFmpeg/PyAV cannot decode.
  Supporting WeChat voice needs an extra SILK-to-PCM step (for example the
  `silk-v3-decoder` project) ahead of `transcribe.py`, and depends on the
  WeChat channel actually exposing the raw voice file. That is out of scope for
  the base setup here.
- First run on a fresh machine downloads the model (~180 MB). Later runs are
  local and fast.
