#!/usr/bin/env python3
"""Transcribe an audio file to text, fully offline.

Pipeline:
  1. Decode the input (any format ffmpeg understands, including Telegram's
     ogg/opus voice notes) into 16 kHz mono PCM, using PyAV. PyAV bundles the
     FFmpeg libraries, so the host machine does not need ffmpeg installed.
  2. Feed that audio to a locally built whisper.cpp binary for recognition.

Everything runs on the machine; nothing is uploaded anywhere.

Usage:
  python transcribe.py <audio-file> [--lang zh] [--model path/to/ggml.bin]

The transcript is printed to stdout (and nothing else on stdout), so callers
can capture it directly.
"""

import argparse
import os
import subprocess
import sys
import tempfile

REPO_ROOT = os.path.dirname(os.path.abspath(__file__))
DEFAULT_MODEL = os.path.join(REPO_ROOT, "models", "ggml-small-q5_1.bin")
WHISPER_CLI = os.path.join(REPO_ROOT, "whisper.cpp", "build", "bin", "whisper-cli")


def decode_to_wav(src_path, dst_path):
    """Decode any audio file into 16 kHz mono 16-bit PCM WAV via PyAV."""
    try:
        import av
        from av.audio.resampler import AudioResampler
    except ImportError:
        sys.exit(
            "PyAV is not installed. Run ./setup.sh first, and invoke this "
            "script with the virtualenv python (.venv/bin/python)."
        )

    in_container = av.open(src_path)
    out_container = av.open(dst_path, "w")
    out_stream = out_container.add_stream("pcm_s16le", rate=16000, layout="mono")
    resampler = AudioResampler(format="s16", layout="mono", rate=16000)

    for frame in in_container.decode(audio=0):
        for resampled in resampler.resample(frame):
            for packet in out_stream.encode(resampled):
                out_container.mux(packet)
    for packet in out_stream.encode(None):
        out_container.mux(packet)

    out_container.close()
    in_container.close()


def run_whisper(wav_path, lang, model_path):
    """Run whisper.cpp on the WAV and return the transcript text."""
    if not os.path.exists(WHISPER_CLI):
        sys.exit(
            f"whisper-cli not found at {WHISPER_CLI}. Run ./setup.sh to build "
            "whisper.cpp first."
        )
    if not os.path.exists(model_path):
        sys.exit(
            f"model not found at {model_path}. Run ./setup.sh to download it, "
            "or pass --model with your own ggml model."
        )

    result = subprocess.run(
        [
            WHISPER_CLI,
            "-m", model_path,
            "-l", lang,
            "-nt",            # no timestamps, transcript text only
            "-f", wav_path,
        ],
        capture_output=True,
        text=True,
    )
    if result.returncode != 0:
        sys.stderr.write(result.stderr)
        sys.exit(f"whisper-cli failed with exit code {result.returncode}")

    return result.stdout.strip()


def main():
    parser = argparse.ArgumentParser(description="Offline audio-to-text.")
    parser.add_argument("audio", help="path to the audio file to transcribe")
    parser.add_argument(
        "--lang", default="zh",
        help="language code passed to whisper.cpp (default: zh; use 'auto' to detect)",
    )
    parser.add_argument(
        "--model", default=DEFAULT_MODEL,
        help="path to a whisper.cpp ggml model (default: models/ggml-small-q5_1.bin)",
    )
    args = parser.parse_args()

    if not os.path.exists(args.audio):
        sys.exit(f"input file not found: {args.audio}")

    with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as tmp:
        wav_path = tmp.name
    try:
        decode_to_wav(args.audio, wav_path)
        transcript = run_whisper(wav_path, args.lang, args.model)
        print(transcript)
    finally:
        if os.path.exists(wav_path):
            os.remove(wav_path)


if __name__ == "__main__":
    main()
