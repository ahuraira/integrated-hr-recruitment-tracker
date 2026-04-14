"""
Migrate existing Azure OpenAI assistants off the retired gpt-4o-mini (2024-07-18)
deployment to the replacement gpt-4.1-mini deployment.

Reads the target model from assistants.json and PATCHes each assistant in-place
so existing assistant IDs (already referenced by App Settings / env vars) keep
working — no ID rotation needed.

Usage:
    python migrate_assistants_model.py              # dry-run, shows planned changes
    python migrate_assistants_model.py --apply      # actually update the assistants
"""

import argparse
import getpass
import json
import os
import sys
from pathlib import Path

from openai import AzureOpenAI

CONFIG_PATH = Path(__file__).parent / "assistants.json"
API_VERSION = "2024-05-01-preview"
ASSISTANT_ENV_KEYS = {
    "cv_data_extractor": "CV_DATA_EXTRACTOR_ASSISTANT_ID",
    "cv_pii_identifier": "CV_PII_IDENTIFIER_ASSISTANT_ID",
    "cv_skills_analyst": "CV_SKILLS_ANALYST_ASSISTANT_ID",
}


def load_config() -> dict:
    with CONFIG_PATH.open("r", encoding="utf-8") as f:
        return json.load(f)


def prompt_missing(name: str, secret: bool = False) -> str:
    value = os.getenv(name)
    if value:
        return value
    return getpass.getpass(f"{name}: ") if secret else input(f"{name}: ").strip()


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--apply", action="store_true",
                        help="Apply changes (default is dry-run)")
    args = parser.parse_args()

    endpoint = prompt_missing("AZURE_OPENAI_ENDPOINT")
    api_key = prompt_missing("AZURE_OPENAI_API_KEY", secret=True)

    client = AzureOpenAI(
        azure_endpoint=endpoint,
        api_key=api_key,
        api_version=API_VERSION,
    )

    config = load_config()
    assistants_cfg = config["assistants"]

    print(f"\nMode: {'APPLY' if args.apply else 'DRY-RUN'}")
    print(f"Config: {CONFIG_PATH}\n")

    exit_code = 0
    for key, cfg in assistants_cfg.items():
        env_key = ASSISTANT_ENV_KEYS.get(key)
        if not env_key:
            print(f"[skip] {key}: no env-var mapping")
            continue

        assistant_id = os.getenv(env_key)
        if not assistant_id:
            assistant_id = input(f"{env_key} (paste assistant ID): ").strip()
        if not assistant_id:
            print(f"[skip] {key}: no assistant ID provided")
            exit_code = 1
            continue

        target_model = cfg["model"]

        try:
            current = client.beta.assistants.retrieve(assistant_id)
        except Exception as e:
            print(f"[error] {key} ({assistant_id}): retrieve failed: {e}")
            exit_code = 1
            continue

        current_model = current.model
        print(f"{key}:")
        print(f"  id:      {assistant_id}")
        print(f"  current: {current_model}")
        print(f"  target:  {target_model}")

        if current_model == target_model:
            print("  -> already on target model, no change\n")
            continue

        if not args.apply:
            print("  -> would update (dry-run)\n")
            continue

        try:
            updated = client.beta.assistants.update(
                assistant_id=assistant_id,
                model=target_model,
            )
            print(f"  -> updated to {updated.model}\n")
        except Exception as e:
            print(f"  -> update FAILED: {e}\n")
            exit_code = 1

    if not args.apply:
        print("Dry-run complete. Re-run with --apply to make changes.")
    return exit_code


if __name__ == "__main__":
    sys.exit(main())
