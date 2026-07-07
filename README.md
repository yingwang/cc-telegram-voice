# cc-telegram-voice

*中文说明见文末 / Chinese documentation is at the bottom of this file.*

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

## Licenses

This repo is MIT. Its dependencies are permissively licensed too: whisper.cpp
is MIT, PyAV is BSD-3-Clause, and the Whisper model weights from OpenAI are MIT.
You are free to use, modify, and redistribute.

---

# cc-telegram-voice（中文说明）

给 [Claude Code](https://claude.com/claude-code) 各通道用的双向语音工具。当有人通过 Telegram 插件发来一条语音时，Claude Code 只能看到一个音频附件，看不到里面说了什么；而 Claude 自己也只能用文字回复。这个小仓库把这两头都补上，只是两个方向在一个关键点上并不相同：

- **语音转文字**（`transcribe.py`）把收到的语音转成文字，**全程在你自己的机器上完成**，音频始终不离开本机。
- **文字转语音**（`speak.py`）把 Claude 的文字回复重新念成一条语音。这一半**不是**离线的：它用的是微软的在线神经语音，因此回复的文字会被发到微软那边去合成。

换句话说，转写这一侧完全在本地，而合成这一侧则是拿这份隐私去换取免费且自然的嗓音。只有当文字本身不介意发出去时，才用语音回复；凡是敏感的内容都留在文字里。

底层都是经过时间检验的开源件，拼装在一起：

- **[PyAV](https://github.com/PyAV-Org/PyAV)** 负责解码收到的音频。PyAV 自带了 FFmpeg 的库，所以你不需要另外装系统级的 ffmpeg。这一点对 Telegram 语音很重要，因为它是 ogg/opus 格式。
- **[whisper.cpp](https://github.com/ggerganov/whisper.cpp)** 负责语音识别，在本地跑一个 Whisper 模型，全程没有任何网络请求。
- **[edge-tts](https://github.com/rany2/edge-tts)** 负责语音合成，走的是微软 Edge 的在线神经语音，免费且无需 API key。它是整套里唯一会连网的部分。

## 安装

```bash
git clone https://github.com/yingwang/cc-telegram-voice.git
cd cc-telegram-voice
./setup.sh
```

`setup.sh` 会创建一个带 PyAV 的 `.venv`，编译 whisper.cpp，并把一个 Whisper 模型（`ggml-small-q5_1`，约 180 MB）下载到 `models/`。它需要 `git`、`cmake` 以及一套 C/C++ 工具链（macOS 上用 `brew install cmake`，Debian/Ubuntu 上用 `apt-get install cmake build-essential`）。重复运行是安全的，已经完成的步骤会自动跳过。

## 单独使用

```bash
./.venv/bin/python transcribe.py path/to/voice.oga --lang zh
```

转写结果只会打印到标准输出，别的什么都不输出，所以你可以直接用管道接走或者存进变量。`--lang` 接受任意 Whisper 语种代码（`zh`、`en` 等），也可以填 `auto` 让它自己识别。`--model` 指向另一个 ggml 模型，需要更高精度就换个更大的，需要更快就换个更小的。

## 在 Claude Code 里用

把附带的两个 skill 拷进你的 Claude Code skills 目录：

```bash
cp -r skills/voice-transcribe skills/voice-reply ~/.claude/skills/
```

然后编辑这两个 `SKILL.md` 文件，把里面的 `/ABSOLUTE/PATH/TO/cc-telegram-voice` 替换成你实际克隆仓库的路径。之后 Claude Code 会自己识别并调用这两个 skill：

- **voice-transcribe**（语音进）：当一条 Telegram 语音到达时，Claude 会下载附件，运行 `transcribe.py`，然后把转写结果当作你亲手打的字来处理。
- **voice-reply**（语音出）：当你开口要一段语音回复时，Claude 会对它的文字回复运行 `speak.py`，再通过通道的 reply 工具把合成出来的 mp3 作为语音附件发回去。

没有任何东西需要你手动去跑，Claude 会在 skill 适用时自动调用脚本。语音回复只在你明确要求时才触发，因此日常的回复仍旧保持文字。

## 用语音回复（TTS）

这是 `transcribe.py` 的反面：把 Claude 的文字回复重新念成一条语音，让一个通道能够双向都走语音。`speak.py` 借助 [edge-tts](https://github.com/rany2/edge-tts) 来完成，它用的是微软 Edge 的神经语音，免费且无需 API key。

```bash
python speak.py "你好，很高兴见到你" --voice zh-CN-YunxiNeural --out reply.mp3
python speak.py --list-voices | grep en-US        # 挑任意嗓音或语种
```

用 `--rate` 和 `--pitch` 调整语速与音调，例如 `--rate=-11% --pitch=-2Hz`。想要更平、更沉稳的节奏，关键其实在于把文本本身写得句内逗号少一些，让停顿都落在句号上，而不是单靠这两个参数。附带的 `voice-reply` skill 已经把这一整套接进了通道回复里。

**隐私上的取舍**：与全程本地的 `transcribe.py` 不同，edge-tts 会把文字发到微软的服务端去合成。凡是不能外传的内容，都请留在文字里，不要走语音。

## 哪些在本地跑，哪些不在

转写完全在本地：没有 API key，不上传，不按分钟计费，语音音频也始终不离开你的机器。代价是识别质量取决于本地模型的水平；需要更准就用 `--model` 换一个更大的 ggml 模型。

合成则正相反。edge-tts 会把你的回复文字发到微软去渲染，换来的是免费、自然的嗓音以及零配置。因此一旦你用了语音回复，这个仓库整体就不再是完全离线的了。把不能外传的内容留在文字而非语音里，或者干脆不用语音回复，保持全程本地。

## 语种

两个方向都支持多语种。进来这一侧，`--lang` 接受任意 Whisper 语种代码（`zh`、`en` 等），也可以填 `auto` 自动识别，中英文夹杂着说也能听懂。出去这一侧，要按你说的语种挑对应的嗓音：中文用 `zh-CN-YunxiNeural`，英文用某个 `en-US-*` 的嗓音，以此类推（`speak.py --list-voices` 可以列出全部）。用中文的嗓音去念一整句英文会听着别扭，所以要换的是嗓音，而不是硬用一个嗓音去跨语种。

## 许可

本仓库采用 MIT 许可。它的依赖也都是宽松许可：whisper.cpp 是 MIT，PyAV 是 BSD-3-Clause，OpenAI 的 Whisper 模型权重是 MIT。你可以自由地使用、修改与再分发。
