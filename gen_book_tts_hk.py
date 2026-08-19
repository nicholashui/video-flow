#!/usr/bin/env python3
import argparse
import json
import os
import re
import sys
import time
from dataclasses import dataclass
from pathlib import Path
from typing import Any

try:
    from dotenv import load_dotenv
except ImportError:
    print("Installing python-dotenv...")
    import subprocess
    subprocess.check_call([sys.executable, "-m", "pip", "install", "python-dotenv"])
    from dotenv import load_dotenv

try:
    import requests
except ImportError:
    print("Installing requests...")
    import subprocess
    subprocess.check_call([sys.executable, "-m", "pip", "install", "requests"])
    import requests

BASE_DIR = Path(__file__).resolve().parent
INPUT_PATH = BASE_DIR / "video-flow-book.script.txt"
FINAL_OUTPUT = BASE_DIR / "video-flow-book.mp3"
SECTION_SEP = "<#0.5#>"
TIMING_TAG_RE = re.compile(r"<#\s*\d+(?:\.\d+)?\s*#>")


def parse_args():
    p = argparse.ArgumentParser(
        description="Generate a Cantonese voice-over MP3 from an HK script text "
                    "(MiniMax TTS), section by section, then combine.")
    p.add_argument("input", nargs="?", default=None,
                   help="input script file (default: video-flow-book.script.txt, "
                        "or $TTS_INPUT if set)")
    p.add_argument("output", nargs="?", default=None,
                   help="final combined MP3 file (default: video-flow-book.mp3, "
                        "or $TTS_OUTPUT if set)")
    p.add_argument("--audio-dir", default=None,
                   help="per-section MP3 directory (default: <output stem>_audio_hk, "
                        "or $TTS_AUDIO_DIR if set)")
    p.add_argument("-i", "--input-flag", dest="input_flag", default=None,
                   help="same as the input positional (alternative form)")
    p.add_argument("-o", "--output-flag", dest="output_flag", default=None,
                   help="same as the output positional (alternative form)")
    return p.parse_args()


def resolve_paths(args):
    """Order of precedence: CLI arg > env var > hardcoded default."""
    inp = Path(args.input or args.input_flag or os.getenv("TTS_INPUT") or INPUT_PATH)
    out = Path(args.output or args.output_flag or os.getenv("TTS_OUTPUT") or FINAL_OUTPUT)
    # audio dir derives from the output stem, dropping a ".hk" suffix so the
    # original no-arg default (training_agent_book_audio_hk) is preserved
    audio = Path(args.audio_dir or os.getenv("TTS_AUDIO_DIR")
                 or (out.parent / f"{out.stem.replace('.hk', '')}_audio_hk"))
    if not inp.is_absolute():
        inp = BASE_DIR / inp
    if not out.is_absolute():
        out = BASE_DIR / out
    if not audio.is_absolute():
        audio = BASE_DIR / audio
    return inp, audio, out

env_dir = BASE_DIR
dotenv_path = env_dir / ".env"
load_dotenv(dotenv_path=dotenv_path)

DEFAULT_ENDPOINT = "https://api.minimax.io/v1/t2a_v2"
LAST_TTS_REQUEST_AT: float | None = None


@dataclass
class MiniMaxTTSConfig:
    voice_id: str = "Cantonese_GentleLady"
    model: str = "speech-2.6-turbo"
    output: Path = Path("output.mp3")
    audio_format: str = "mp3"
    response_format: str = "hex"
    speed: float = 1.0
    volume: float = 1.0
    pitch: int = 0
    emotion: str | None = "fluent"
    language_boost: str | None = "Chinese,Yue"
    sample_rate: int = 32000
    bitrate: int = 128000
    channel: int = 1
    timeout: int = 300


def first_non_empty(*values: Any) -> Any:
    for value in values:
        if value not in (None, "", [], {}):
            return value
    return None


def ensure_success(payload: dict[str, Any]) -> None:
    base_resp = payload.get("base_resp") or {}
    status_code = first_non_empty(
        base_resp.get("status_code"),
        base_resp.get("code"),
        payload.get("status_code"),
        payload.get("code"),
    )
    if status_code in (None, 0, "0"):
        return

    message = first_non_empty(
        base_resp.get("status_msg"),
        base_resp.get("message"),
        payload.get("message"),
        payload.get("msg"),
        "MiniMax returned an unknown error.",
    )
    raise RuntimeError(f"MiniMax API error {status_code}: {message}")


def build_request(text: str, config: MiniMaxTTSConfig) -> dict[str, Any]:
    forced_emotion = "fluent"
    voice_setting: dict[str, Any] = {
        "voice_id": config.voice_id,
        "speed": config.speed,
        "vol": config.volume,
        "pitch": config.pitch,
        "emotion": forced_emotion,
    }

    audio_setting: dict[str, Any] = {
        "audio_sample_rate": config.sample_rate,
        "format": config.audio_format,
        "channel": config.channel,
    }
    if config.audio_format == "mp3":
        audio_setting["bitrate"] = config.bitrate

    payload: dict[str, Any] = {
        "model": config.model,
        "text": text,
        "stream": False,
        "output_format": config.response_format,
        "voice_setting": voice_setting,
        "audio_setting": audio_setting,
    }
    if config.language_boost:
        payload["language_boost"] = config.language_boost
    return payload


def throttle_tts_requests() -> None:
    global LAST_TTS_REQUEST_AT

    delay_seconds = float(os.getenv("MINIMAX_REQUEST_DELAY_SECONDS", "5"))
    if delay_seconds <= 0:
        return

    if LAST_TTS_REQUEST_AT is not None:
        elapsed = time.monotonic() - LAST_TTS_REQUEST_AT
        remaining = delay_seconds - elapsed
        if remaining > 0:
            print(f"  Waiting {remaining:.1f}s before next TTS request...")
            time.sleep(remaining)


def is_tpm_rate_limit(payload: dict[str, Any]) -> bool:
    base_resp = payload.get("base_resp") or {}
    status_code = first_non_empty(
        base_resp.get("status_code"),
        base_resp.get("code"),
        payload.get("status_code"),
        payload.get("code"),
    )
    message = str(
        first_non_empty(
            base_resp.get("status_msg"),
            base_resp.get("message"),
            payload.get("message"),
            payload.get("msg"),
            "",
        )
    ).lower()
    return str(status_code) == "1039" or "rate limit exceeded" in message or "tpm" in message


def audio_bytes_from_hex(data: dict[str, Any]) -> bytes:
    audio_hex = first_non_empty(
        data.get("audio"),
        data.get("audio_hex"),
        data.get("audio_data"),
        data.get("hex"),
    )
    if not isinstance(audio_hex, str):
        raise RuntimeError(
            f"Could not find hex audio data in response. Keys: {sorted(data.keys())}"
        )
    return bytes.fromhex(audio_hex)


def audio_bytes_from_url(data: dict[str, Any], timeout: int) -> bytes:
    audio_url = first_non_empty(
        data.get("audio"),
        data.get("audio_url"),
        data.get("url"),
    )
    if not isinstance(audio_url, str):
        raise RuntimeError(
            f"Could not find audio URL in response. Keys: {sorted(data.keys())}"
        )

    response = requests.get(audio_url, timeout=timeout)
    response.raise_for_status()
    return response.content


def extract_audio_bytes(
    data: dict[str, Any], response_format: str, timeout: int
) -> bytes:
    if response_format == "hex":
        return audio_bytes_from_hex(data)
    return audio_bytes_from_url(data, timeout)


def request_audio_result(text: str, config: MiniMaxTTSConfig) -> dict[str, Any]:
    global LAST_TTS_REQUEST_AT

    api_key = os.getenv("MINIMAX_API_KEY")
    if not api_key:
        raise RuntimeError("Set MINIMAX_API_KEY in your environment or .env file.")

    if not text:
        raise RuntimeError("Input text is empty.")

    endpoint = os.getenv("MINIMAX_TTS_URL", DEFAULT_ENDPOINT)
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json",
    }
    payload = build_request(text, config)

    _forced = "fluent"
    vs = payload.get("voice_setting") or {}
    if vs.get("emotion") != _forced:
        print(f"  ! emotion override in payload: was {vs.get('emotion')!r}, forcing {_forced!r}")
        vs["emotion"] = _forced

    max_retries = int(os.getenv("MINIMAX_RATE_LIMIT_RETRIES", "8"))
    retry_delay_seconds = float(os.getenv("MINIMAX_RETRY_DELAY_SECONDS", "12"))
    retry_delay_step_seconds = float(os.getenv("MINIMAX_RETRY_DELAY_STEP_SECONDS", "6"))

    for attempt in range(max_retries + 1):
        throttle_tts_requests()

        response = requests.post(
            endpoint,
            headers=headers,
            json=payload,
            timeout=config.timeout,
        )
        LAST_TTS_REQUEST_AT = time.monotonic()
        response.raise_for_status()

        result = response.json()
        if is_tpm_rate_limit(result):
            if attempt >= max_retries:
                ensure_success(result)
            wait_seconds = retry_delay_seconds + (attempt * retry_delay_step_seconds)
            print(
                f"  MiniMax TPM rate limit hit, retrying in {wait_seconds:.1f}s "
                f"(attempt {attempt + 1}/{max_retries + 1})..."
            )
            time.sleep(wait_seconds)
            continue

        ensure_success(result)

        data = result.get("data")
        if not isinstance(data, dict):
            raise RuntimeError(
                f"MiniMax response did not include a data object: {json.dumps(result)}"
            )
        return result

    raise RuntimeError("MiniMax request failed after retries.")


def _timing_tag_spans(text: str) -> list[tuple[int, int]]:
    return [(m.start(), m.end()) for m in TIMING_TAG_RE.finditer(text)]


def _is_inside_timing_tag(pos: int, spans: list[tuple[int, int]]) -> bool:
    for s, e in spans:
        if s < pos < e:
            return True
    return False


def split_text_for_tts(text: str, max_chars: int) -> list[str]:
    if len(text) <= max_chars:
        return [text]

    spans = _timing_tag_spans(text)
    chunks: list[str] = []
    current = ""

    def flush() -> None:
        nonlocal current
        if current.strip():
            chunks.append(current.strip())
        current = ""

    def append_piece(piece: str) -> None:
        nonlocal current
        piece = piece.strip()
        if not piece:
            return
        candidate = f"{current}\n\n{piece}" if current else piece
        if len(candidate) <= max_chars:
            current = candidate
            return
        flush()
        if len(piece) <= max_chars:
            current = piece
            return

        sentence_parts = re.split(r"(?<=[.!?。！？])\s+", piece)
        if len(sentence_parts) > 1:
            for part in sentence_parts:
                append_piece(part)
            return

        words = piece.split()
        if len(words) > 1:
            line = ""
            for word in words:
                candidate_line = f"{line} {word}".strip()
                if len(candidate_line) <= max_chars:
                    line = candidate_line
                else:
                    if line:
                        chunks.append(line)
                    line = word
            if line:
                chunks.append(line)
            return

        start = 0
        while start < len(piece):
            end = min(start + max_chars, len(piece))
            while end < len(piece) and _is_inside_timing_tag(end, spans):
                end += 1
            chunks.append(piece[start:end])
            start = end

    for paragraph in re.split(r"\n\s*\n", text.strip()):
        append_piece(paragraph)

    flush()
    return chunks or [text]


def generate_audio_bytes(text: str, config: MiniMaxTTSConfig) -> tuple[bytes, list[str]]:
    max_text_length = int(os.getenv("MINIMAX_MAX_TEXT_LENGTH", "3000"))
    chunks = split_text_for_tts(text, max_text_length)
    audio_parts: list[bytes] = []
    trace_ids: list[str] = []

    for index, chunk in enumerate(chunks, start=1):
        if len(chunks) > 1:
            print(f"  TTS chunk {index}/{len(chunks)} ({len(chunk)} chars)")
        result = request_audio_result(chunk, config)
        data = result["data"]
        audio_parts.append(
            extract_audio_bytes(data, config.response_format, config.timeout)
        )

        trace_id = result.get("trace_id")
        if isinstance(trace_id, str) and trace_id:
            trace_ids.append(trace_id)

    return b"".join(audio_parts), trace_ids


def load_script(path: Path) -> str:
    if not path.exists():
        raise FileNotFoundError(f"Script file not found: {path}")
    with open(path, "r", encoding="utf-8") as f:
        return f.read()


def split_into_sections(full_text: str) -> list[tuple[str, str | None]]:
    tokens = re.split(r"(<#\s*\d+(?:\.\d+)?\s*#>)", full_text)
    results: list[tuple[str, str | None]] = []
    pending_tag: str | None = None
    for tok in tokens:
        if not tok:
            continue
        if TIMING_TAG_RE.fullmatch(tok):
            pending_tag = tok.strip()
        else:
            s = tok.strip()
            if s:
                results.append((s, pending_tag))
                pending_tag = None
    return results


def main():
    args = parse_args()
    input_path, audio_dir, output_path = resolve_paths(args)
    print(f"Input script: {input_path}")
    print(f"Audio dir:    {audio_dir}")
    print(f"Output MP3:   {output_path}")

    print(f"Loading Cantonese script from: {input_path}")
    full_text = load_script(input_path)
    print(f"Total script length: {len(full_text)} chars")

    found_tags = sorted(set(TIMING_TAG_RE.findall(full_text)))
    print(f"\nDetected timing tags in script: {found_tags or '(none)'}")
    print(
        "Timing tags (e.g. <#0.5#>) will be PASSED THROUGH to MiniMax TTS as-is "
        "so MiniMax renders the silence inside the audio itself."
    )

    print(f"\nSplitting into sections by timing tag (<#N#>)...")
    sections = split_into_sections(full_text)
    print(f"Found {len(sections)} sections")
    for i, (s, tag) in enumerate(sections):
        preview = s[:80].replace("\n", " ")
        tag_info = f" | prefix-tag={tag!r}" if tag else " | prefix-tag=(none, first section)"
        print(f"  [{i+1:3d}] {len(s):>5d} chars{tag_info} | {preview}...")

    print(f"\nOutput directory: {audio_dir}")
    audio_dir.mkdir(parents=True, exist_ok=True)

    combined_bytes: list[bytes] = []
    FORCED_EMOTION = "fluent"
    config = MiniMaxTTSConfig(emotion=FORCED_EMOTION)
    print(f"TTS config: voice={config.voice_id}, speed={config.speed}, "
          f"lang_boost={config.language_boost}, emotion=**{FORCED_EMOTION}** (locked for every section/chunk)")

    skip_existing = True

    for i, (section_text, prefix_tag) in enumerate(sections):
        sidx = i + 1
        section_file = audio_dir / f"section_{sidx:03d}.mp3"

        tts_text = f"{prefix_tag}{section_text}" if prefix_tag else section_text

        if skip_existing and section_file.exists():
            print(f"\n=== Section {sidx}/{len(sections)}: already exists -> skip ===")
            if prefix_tag:
                print(f"  (Would have sent prefix timing tag to TTS: {prefix_tag!r} — baked into existing audio at generation time)")
            data = section_file.read_bytes()
            combined_bytes.append(data)
            print(f"  Loaded existing: {len(data)} bytes")
            continue

        tag_note = f" | prefix-timing-tag-to-TTS={prefix_tag!r}" if prefix_tag else " | prefix-timing-tag-to-TTS=(none)"
        print(f"\n=== Section {sidx}/{len(sections)} ({len(tts_text)} chars) | emotion={FORCED_EMOTION}{tag_note} ===")
        if prefix_tag:
            print(f"  -> Sending to MiniMax TTS with LEADING timing tag: {prefix_tag!r}")
            print(f"     (MiniMax will render {prefix_tag} as a real silence pause BEFORE this section's speech)")
        section_config = MiniMaxTTSConfig(output=section_file, emotion=FORCED_EMOTION)
        try:
            audio_data, trace_ids = generate_audio_bytes(tts_text, section_config)
            section_file.write_bytes(audio_data)
            combined_bytes.append(audio_data)
            tag_done = f" [tag-to-TTS={prefix_tag!r}]" if prefix_tag else ""
            print(f"  Saved: {section_file} ({len(audio_data)} bytes) [emotion={FORCED_EMOTION}]{tag_done}")
            for tid in trace_ids:
                print(f"  trace_id: {tid}")
        except Exception as e:
            print(f"  ERROR generating section {sidx}: {e}")
            raise

        inter_delay = float(os.getenv("MINIMAX_REQUEST_DELAY_SECONDS", "5"))
        if inter_delay > 0 and sidx < len(sections):
            pass

    print(f"\nCombining {len(combined_bytes)} MP3 sections...")
    final_data = b"".join(combined_bytes)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_bytes(final_data)
    print(f"Final combined audio saved: {output_path} ({len(final_data)} bytes)")
    print(
        "  Note: inter-section silence (<#N#>) was rendered BY MiniMax TTS (inside each section_###.mp3 "
        "after the 1st) using the real timing tag — NOT by relying on binary-concat gap."
    )

    print("\nDone!")
    print(f"  Per-section MP3s: {audio_dir}")
    print(f"  Combined MP3:     {output_path}")


if __name__ == "__main__":
    main()
