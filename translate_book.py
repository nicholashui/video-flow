import os
import re
import time
import sys
import random
import argparse
from pathlib import Path

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
ENV_PATH = BASE_DIR / ".env"
SYSTEM_PROMPT_PATH = BASE_DIR / "ytscript.txt"
INPUT_MD_PATH = BASE_DIR / "video-flow-book.md"
OUTPUT_PATH = BASE_DIR / "video-flow-book.script.txt"
SEPARATOR = "<#0.5#>"


def parse_args():
    p = argparse.ArgumentParser(
        description="Translate a markdown book into a Cantonese voice-over script (HK).")
    p.add_argument("input", nargs="?", default=None,
                   help="input markdown file (default: video-flow-book.md, "
                        "or $BOOK_INPUT if set)")
    p.add_argument("output", nargs="?", default=None,
                   help="output script file (default: video-flow-book.script.txt, "
                        "or $BOOK_OUTPUT if set)")
    p.add_argument("-i", "--input-flag", dest="input_flag", default=None,
                   help="same as the input positional (alternative form)")
    p.add_argument("-o", "--output-flag", dest="output_flag", default=None,
                   help="same as the output positional (alternative form)")
    args = p.parse_args()
    return args


def resolve_paths(args):
    """Order of precedence: CLI arg > env var > hardcoded default."""
    inp = args.input or args.input_flag or os.getenv("BOOK_INPUT") or INPUT_MD_PATH
    out = args.output or args.output_flag or os.getenv("BOOK_OUTPUT") or OUTPUT_PATH
    inp = Path(inp)
    out = Path(out)
    if not inp.is_absolute():
        inp = BASE_DIR / inp
    if not out.is_absolute():
        out = BASE_DIR / out
    return inp, out


def load_env():
    if ENV_PATH.exists():
        load_dotenv(ENV_PATH)
    api_key = os.getenv("POE_API_KEY")
    base_url = os.getenv("POE_BASE_URL", "https://api.poe.com/v1")
    model = os.getenv("POE_BASE_MODEL", "grok-4.1-fast-non-reasoning")
    if not api_key:
        raise ValueError("POE_API_KEY not found in .env or environment")
    return api_key, base_url.rstrip("/"), model


def load_system_prompt():
    if not SYSTEM_PROMPT_PATH.exists():
        raise FileNotFoundError(f"System prompt file not found: {SYSTEM_PROMPT_PATH}")
    with open(SYSTEM_PROMPT_PATH, "r", encoding="utf-8") as f:
        return f.read().strip()


def extract_transition_words(system_prompt):
    in_code_block = False
    code_content = []
    for line in system_prompt.splitlines():
        stripped = line.strip()
        if stripped.startswith("```"):
            if not in_code_block:
                in_code_block = True
            else:
                in_code_block = False
            continue
        if in_code_block:
            code_content.append(line)
    block = "".join(code_content)
    raw = [t.strip() for t in re.split(r"[／／、,，]", block) if t.strip()]
    seen = set()
    cleaned = []
    for w in raw:
        w = w.strip("。.！!？?；;：:\"'` ")
        if w and w not in seen:
            seen.add(w)
            cleaned.append(w)
    if not cleaned:
        cleaned = ["跟住我哋講嘅係", "好啦", "然後", "另外", "最後"]
    return cleaned


def build_transition_instruction(transition_words, section_index, total_sections):
    pool = list(transition_words)
    random.shuffle(pool)
    num_for_opening = 1
    num_for_mid = min(6, max(3, len(pool) // 4))
    opening = pool[:num_for_opening]
    remaining = pool[num_for_opening:]
    if len(remaining) < num_for_mid:
        random.shuffle(pool)
        mid_pool = pool[:num_for_mid]
    else:
        mid_pool = remaining[:num_for_mid]
    random.shuffle(mid_pool)

    open_str = "、".join(opening)
    mid_str = "、".join(mid_pool)
    instruction = (
        f"\n\n【本節隨機抽選過場字指令 — 必須嚴格遵守，唔可以用其他】\n"
        f"呢一節係第 {section_index}/{total_sections} 節，系統已經幫你隨機抽好要用嘅過場字，"
        f"你只可以用以下指定嘅字，絕對唔可以用列表入面其他過場字：\n"
        f"・開頭一定要用：【{open_str}】 或者由開頭變化出嚟嘅同義句式\n"
        f"・中間過渡可以用：【{mid_str}】\n"
        f"・嚴禁再用「跟住我哋講嘅係」除非佢出現喺上面指定列表入面\n"
        f"・每次過渡都要轉另一個字，唔好重複用同一個\n"
    )
    return instruction, opening, mid_pool


def load_markdown(path):
    if not path.exists():
        raise FileNotFoundError(f"Markdown file not found: {path}")
    with open(path, "r", encoding="utf-8") as f:
        return f.read()


def split_markdown_by_headings(md_text):
    lines = md_text.splitlines(keepends=True)
    heading_re = re.compile(r"^(#{1,6})\s+(.+)$")

    sections = []
    current_lines = []
    current_heading = None

    for line in lines:
        m = heading_re.match(line.rstrip("\n").rstrip("\r"))
        if m:
            if current_lines:
                if current_heading is not None or any(l.strip() for l in current_lines):
                    sections.append("".join(current_lines).rstrip())
            current_lines = [line]
            current_heading = m.group(2)
        else:
            current_lines.append(line)

    if current_lines:
        if current_heading is not None or any(l.strip() for l in current_lines):
            sections.append("".join(current_lines).rstrip())

    non_empty = []
    for s in sections:
        if s.strip():
            non_empty.append(s)
    return non_empty


def call_llm(api_key, base_url, model, system_prompt, user_content, max_retries=3, retry_delay=5):
    url = f"{base_url}/chat/completions"
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json",
    }
    payload = {
        "model": model,
        "messages": [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_content},
        ],
        "temperature": 0.7,
    }

    for attempt in range(1, max_retries + 1):
        try:
            resp = requests.post(url, headers=headers, json=payload, timeout=300)
            resp.raise_for_status()
            data = resp.json()
            if "choices" in data and len(data["choices"]) > 0:
                return data["choices"][0]["message"]["content"].strip()
            else:
                raise ValueError(f"Unexpected API response: {data}")
        except Exception as e:
            print(f"  Attempt {attempt}/{max_retries} failed: {e}")
            if attempt < max_retries:
                print(f"  Retrying in {retry_delay}s...")
                time.sleep(retry_delay)
            else:
                raise


def main():
    args = parse_args()
    input_path, output_path = resolve_paths(args)
    print(f"Input:  {input_path}")
    print(f"Output: {output_path}")

    print("Loading environment...")
    api_key, base_url, model = load_env()
    print(f"Model: {model}")

    print("Loading system prompt...")
    system_prompt = load_system_prompt()
    print(f"System prompt length: {len(system_prompt)} chars")

    print("Extracting transition words...")
    transition_words = extract_transition_words(system_prompt)
    print(f"Found {len(transition_words)} transition words:")
    print(f"  {', '.join(transition_words)}")

    print("Loading markdown...")
    md_text = load_markdown(input_path)
    print(f"Markdown length: {len(md_text)} chars")

    print("Splitting by headings...")
    sections = split_markdown_by_headings(md_text)
    print(f"Found {len(sections)} sections")
    for i, s in enumerate(sections):
        first_line = s.splitlines()[0][:80] if s.splitlines() else "(empty)"
        print(f"  [{i+1}] {len(s)} chars - {first_line}")

    print("\nTranslating sections (this may take a while)...")
    results = []
    for i, section in enumerate(sections):
        sidx = i + 1
        total = len(sections)
        trans_instr, opening, mid_pool = build_transition_instruction(transition_words, sidx, total)
        print(f"\nProcessing section {sidx}/{total} ({len(section)} chars)...")
        print(f"  Random opening: 「{' / '.join(opening)}」")
        print(f"  Random mid:     「{' / '.join(mid_pool)}」")
        enriched_user_content = section + trans_instr
        try:
            translated = call_llm(api_key, base_url, model, system_prompt, enriched_user_content)
            results.append(translated)
            print(f"  Translated: {len(translated)} chars")
            first_preview = translated[:120].replace("\n", " ")
            print(f"  Preview: {first_preview}...")
        except Exception as e:
            print(f"  ERROR on section {sidx}: {e}")
            fallback = f"[Translation failed for section {sidx}: {e}]"
            results.append(fallback)
        time.sleep(1)

    print(f"\nCombining {len(results)} sections with separator '{SEPARATOR}'...")
    output = SEPARATOR.join(results)

    print(f"Writing output to {output_path}...")
    output_path.parent.mkdir(parents=True, exist_ok=True)
    with open(output_path, "w", encoding="utf-8") as f:
        f.write(output)

    print(f"Done! Output written to {output_path}")
    print(f"Total output length: {len(output)} chars")


if __name__ == "__main__":
    main()
