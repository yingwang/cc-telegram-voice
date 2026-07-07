# cc-telegram-voice

Offline voice-to-text for [Claude Code](https://claude.com/claude-code) channels.
When someone sends a voice note over the Telegram plugin, Claude Code can only
see an audio attachment, not its contents. This little repo transcribes that
audio **entirely on your own machine** so Claude can read what was said and
reply, with no audio ever leaving the computer.

It is two well-worn open-source pieces wired together:

- **[PyAV](https://github.com/PyAV-Org/PyAV)** decodes the incoming audio.
  PyAV bundles the FFmpeg libraries, so you do not need a system ffmpeg. This
  matters for Telegram voice notes, which are ogg/opus.
- **[whisper.cpp](https://github.com/ggerganov/whisper.cpp)** does the speech
  recognition, running a local Whisper model with no network calls.

## Install

```bash
git clone https://github.com/yingwang/cc-telegram-voice.git
cd cc-telegram-voice
./setup.sh
```

`setup.sh` creates a `.venv` with PyAV, builds whisper.cpp, and downloads a
Whisper model (`ggml-small-q5_1`, ~180 MB) into `models/`. It needs `git`,
`cmake`, and a C/C++ toolchain (`brew install cmake` on macOS;
`apt-get install cmake build-essential` on Debian/Ubuntu). Re-running is safe;
each step is skipped if already done.

## Use on its own

```bash
./.venv/bin/python transcribe.py path/to/voice.oga --lang zh
```

The transcript is printed to stdout and nothing else, so you can capture it in a
pipe or a variable. `--lang` takes any Whisper language code (`zh`, `en`, ...)
or `auto` to detect. `--model` points at a different ggml model if you want a
larger one for accuracy or a tiny one for speed.

## Use inside Claude Code

Copy the bundled skill into your Claude Code skills directory:

```bash
cp -r skills/voice-transcribe ~/.claude/skills/
```

Then edit `~/.claude/skills/voice-transcribe/SKILL.md` and replace
`/ABSOLUTE/PATH/TO/cc-telegram-voice` with the real path where you cloned this
repo. After that, when a Telegram voice note arrives, Claude Code will download
the attachment, run the transcriber, and treat the result as if you had typed
it.

## Replying with voice (TTS)

The flip side of `transcribe.py`: turn Claude's text reply back into a voice
note, so a channel can be two-way voice. `speak.py` does this with
[edge-tts](https://github.com/rany2/edge-tts), Microsoft Edge's neural voices,
which are free and need no API key.

```bash
python speak.py "你好，很高兴见到你" --voice zh-CN-YunxiNeural --out reply.mp3
python speak.py --list-voices | grep en-US        # pick any voice or language
```

Tune pace and tone with `--rate` and `--pitch`, e.g. `--rate=-11% --pitch=-2Hz`.
A flatter, calmer cadence comes mostly from writing the text with few internal
commas, so the pauses fall on full stops, rather than from those flags alone.
The bundled `voice-reply` skill wires this into a channel reply.

**Privacy tradeoff:** unlike `transcribe.py`, which is fully local, edge-tts
sends the text to Microsoft's endpoint to synthesize it. Keep anything you must
not share in text, not voice.

## Why offline

The transcription side runs locally. No API keys, no upload, no per-minute cost, and voice
audio never leaves your machine. The tradeoff is that recognition quality is
whatever the local model gives you; bump to a larger ggml model with `--model`
if you need more accuracy.

## A note on WeChat voice

WeChat voice messages use the SILK codec, which FFmpeg (and therefore PyAV)
cannot decode. To support WeChat voice you would add a SILK-to-PCM step (for
example the [silk-v3-decoder](https://github.com/kn007/silk-v3-decoder)
project) before `transcribe.py`, and it also depends on the WeChat channel
exposing the raw voice file. That path is untested here and left out on purpose.

## Licenses

This repo is MIT. Its dependencies are permissively licensed too: whisper.cpp
is MIT, PyAV is BSD-3-Clause, and the Whisper model weights from OpenAI are MIT.
You are free to use, modify, and redistribute.
