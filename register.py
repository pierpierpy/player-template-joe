#!/usr/bin/env python3
import os
import sys

import requests


def _resolve_player_name() -> str:
    env_name = os.getenv("PLAYER_NAME", "").strip()
    if env_name:
        return env_name
    if len(sys.argv) > 1 and sys.argv[1].strip():
        return sys.argv[1].strip()
    raise SystemExit("Provide a player name via PLAYER_NAME env var or first CLI argument.")


def main() -> None:
    server_url = os.getenv("SERVER_URL", "https://game-platform-v2-914970891924.us-central1.run.app").rstrip("/")
    github_token = os.getenv("GITHUB_TOKEN", "").strip()
    player_name = _resolve_player_name()

    if not github_token:
        raise SystemExit("GITHUB_TOKEN environment variable not set")

    try:
        response = requests.post(
            f"{server_url}/register",
            headers={
                "Content-Type": "application/json",
                "Authorization": f"Bearer {github_token}",
            },
            json={"player_name": player_name},
            timeout=10,
        )
    except Exception as exc:
        raise SystemExit(f"Registration error: {exc}") from exc

    if not response.ok:
        raise SystemExit(f"Registration failed: {response.status_code} {response.text}")

    try:
        payload = response.json()
    except ValueError:
        print("Registration succeeded but response was not JSON.")
        return

    status = (payload.get("status") or "").lower()
    if status == "registered":
        print(f"Player '{payload.get('player_name')}' registered with id {payload.get('player_id')}.")
    elif status == "already_registered":
        print(f"Player '{payload.get('player_name')}' already registered. Using id {payload.get('player_id')}.")
    else:
        print(f"Registration response: {payload}")


if __name__ == "__main__":
    main()
