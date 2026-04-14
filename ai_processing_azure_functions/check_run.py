"""
Inspect a specific Azure OpenAI Assistant run.
Usage:  python check_run.py
"""

import getpass
import json
import sys
import urllib.request
import urllib.error

ENDPOINT = "https://oai-mpr-assistant.openai.azure.com"
API_VERSION = "2024-12-01-preview"
THREAD_ID = "thread_SWwogSHSA04YthGv1tBy7fHZ"
RUN_ID = "run_ZQhSPJy8jCKkbEAKnJLiOTIp"


def get(url: str, api_key: str) -> dict:
    req = urllib.request.Request(url, headers={"api-key": api_key})
    try:
        with urllib.request.urlopen(req, timeout=30) as resp:
            return json.loads(resp.read().decode())
    except urllib.error.HTTPError as e:
        body = e.read().decode(errors="replace")
        print(f"\nHTTP {e.code} calling {url}\n{body}", file=sys.stderr)
        sys.exit(1)


def main() -> None:
    api_key = getpass.getpass("Azure OpenAI API key: ").strip()
    if not api_key:
        print("No key provided.", file=sys.stderr)
        sys.exit(1)

    run_url = f"{ENDPOINT}/openai/threads/{THREAD_ID}/runs/{RUN_ID}?api-version={API_VERSION}"
    steps_url = f"{ENDPOINT}/openai/threads/{THREAD_ID}/runs/{RUN_ID}/steps?api-version={API_VERSION}"
    msgs_url = f"{ENDPOINT}/openai/threads/{THREAD_ID}/messages?api-version={API_VERSION}&limit=5&order=desc"
    all_runs_url = f"{ENDPOINT}/openai/threads/{THREAD_ID}/runs?api-version={API_VERSION}&limit=20&order=desc"

    print("\n=== ALL RUNS ON THIS THREAD (most recent first) ===")
    all_runs = get(all_runs_url, api_key)
    for r in all_runs.get("data", []):
        print(f"- {r.get('id')}  status={r.get('status'):<12}  "
              f"created={r.get('created_at')}  started={r.get('started_at')}  "
              f"model={r.get('model')}  last_error={r.get('last_error')}")

    print("\n=== RUN ===")
    run = get(run_url, api_key)
    summary_keys = [
        "id", "status", "model", "created_at", "started_at",
        "completed_at", "cancelled_at", "failed_at", "expires_at",
        "last_error", "required_action", "usage", "instructions",
    ]
    for k in summary_keys:
        if k in run:
            print(f"{k}: {json.dumps(run[k], indent=2) if isinstance(run[k], (dict, list)) else run[k]}")

    print("\n=== RUN STEPS ===")
    steps = get(steps_url, api_key)
    for s in steps.get("data", []):
        print(f"- step {s.get('id')}  type={s.get('type')}  status={s.get('status')}  "
              f"created={s.get('created_at')}  completed={s.get('completed_at')}  "
              f"last_error={s.get('last_error')}")

    print("\n=== LAST MESSAGES ON THREAD ===")
    msgs = get(msgs_url, api_key)
    for m in msgs.get("data", []):
        content = m.get("content", [])
        text = ""
        for c in content:
            if c.get("type") == "text":
                text = c.get("text", {}).get("value", "")[:200]
                break
        print(f"- {m.get('role')} @ {m.get('created_at')}  run={m.get('run_id')}  text={text!r}")

    print("\nDone.")


if __name__ == "__main__":
    main()
