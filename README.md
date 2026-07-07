# cc-telegram-voice

*中文说明见 [README.zh.md](README.zh.md).*

Two-way voice for [Claude Code](https://claude.com/claude-code) channels. When
someone sends a voice note over the Telegram plugin, Claude Code sees only an
audio attachment, not its contents; and on its own Claude can only reply in
text. This little repo closes both gaps, but the two directions differ in one
important way:

- **Speech in** (`transcribe.py`) turns an incoming voice note into text
  **entirely on your own machine**. No audio ever leaves the computer.
- **Speech out** (`speak.py`) turns Claude's text reply back into a voice note.
  This half is **not** offline: it uses Microsoft's online neural voices, so the
  reply text is sent to Microsoft to be synthesized.

So the transcription side is fully local, while the synthesis side trades that
privacy for free, natural-sounding voices. Reach for voice-out only with text
you are comfortable sending out; keep anything sensitive in text.

The pieces are all well-worn open source, wired together:

- **[PyAV](https://github.com/PyAV-Org/PyAV)** decodes the incoming audio.
  PyAV bundles the FFmpeg libraries, so you do not need a system ffmpeg. This
  matters for Telegram voice notes, which are ogg/opus.
- **[whisper.cpp](https://github.com/ggerganov/whisper.cpp)** does the speech
  recognition, running a local Whisper model with no network calls.
- **[edge-tts](https://github.com/rany2/edge-tts)** does the speech synthesis
  through Microsoft Edge's online neural voices, which are free and need no API
  key. This is the one part that talks to the network.

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

Copy the bundled skills into your Claude Code skills directory:

```bash
cp -r skills/voice-transcribe skills/voice-reply ~/.claude/skills/
```

Then edit both `SKILL.md` files and replace `/ABSOLUTE/PATH/TO/cc-telegram-voice`
with the real path where you cloned this repo. After that Claude Code picks the
skills up on its own:

- **voice-transcribe** (speech in): when a Telegram voice note arrives, Claude
  downloads the attachment, runs `transcribe.py`, and treats the transcript as
  if you had typed it.
- **voice-reply** (speech out): when you ask for a spoken answer, Claude runs
  `speak.py` on its reply and sends the resulting mp3 back through the channel's
  reply tool as a voice attachment.

There is nothing to run by hand; Claude invokes the scripts when the skill
applies. Voice-out only fires when you explicitly ask for it, so ordinary
replies stay text.

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

## What runs locally, what does not

Transcription is fully local: no API keys, no upload, no per-minute cost, and the
voice audio never leaves your machine. The tradeoff is that recognition quality is
whatever the local model gives you; bump to a larger ggml model with `--model`
if you need more accuracy.

Synthesis is the opposite. edge-tts sends your reply text to Microsoft to render
it, in exchange for free, natural voices and no setup. So the repo as a whole is
not fully offline once you use voice-out. Keep anything you must not share in
text rather than voice, or skip voice-out entirely and stay fully local.

## Languages

Both directions are multilingual. On the way in, `--lang` takes any Whisper
language code (`zh`, `en`, ...) or `auto` to detect, and mixed Chinese/English
speech is understood. On the way out, pick a voice that matches the language you
are speaking: `zh-CN-YunxiNeural` for Chinese, an `en-US-*` voice for English,
and so on (`speak.py --list-voices`). A Chinese voice reading a full English
sentence will sound off, so switch voices rather than languages.

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
