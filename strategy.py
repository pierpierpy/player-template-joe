#!/usr/bin/env python3
import os
import random
from functools import lru_cache
from typing import Any, Dict, List, Optional

import requests


SERVER_URL = os.getenv("SERVER_URL")
GITHUB_TOKEN = os.getenv("GITHUB_TOKEN")


def random_direction() -> str:
    return random.choice(["0", "1", "2"])


@lru_cache(maxsize=1)
def _token_owner() -> Optional[str]:
    if not GITHUB_TOKEN:
        return None
    try:
        response = requests.get(
            "https://api.github.com/user",
            headers={
                "Accept": "application/vnd.github+json",
                "Authorization": f"Bearer {GITHUB_TOKEN}",
            },
            timeout=10,
        )
    except requests.RequestException:
        return None

    if not response.ok:
        return None

    try:
        login = response.json().get("login")
    except ValueError:
        return None

    return login.lower() if isinstance(login, str) else None


def extract_opponent_ids(state: Dict[str, Any]) -> List[str]:
    players = state.get("players") or []
    skip_login = _token_owner()
    ids: List[str] = []
    for player in players:
        pid = player.get("player_id") or player.get("playerId")
        if not pid:
            continue
        owner = player.get("player_github") or player.get("playerGithub")
        if skip_login and isinstance(owner, str) and owner.lower() == skip_login:
            continue
        ids.append(str(pid))
    return ids


def strategy(state: Dict[str, Any]) -> Dict[str, Dict[str, str]]:
    opponent_ids = extract_opponent_ids(state)
    shoot = {pid: random_direction() for pid in opponent_ids}
    keep = {pid: random_direction() for pid in opponent_ids}
    if not shoot:
        direction = random_direction()
        shoot["*"] = direction
        keep["*"] = direction
    return {"shoot": shoot, "keep": keep}


def main() -> None:
    if not SERVER_URL:
        raise SystemExit("SERVER_URL env var required")

    status = requests.get(f"{SERVER_URL}/status", timeout=10)
    status.raise_for_status()
    action = strategy(status.json())

    headers = {"Content-Type": "application/json"}
    if GITHUB_TOKEN:
        headers["Authorization"] = f"Bearer {GITHUB_TOKEN}"

    response = requests.post(
        f"{SERVER_URL}/action",
        headers=headers,
        json={"action": action},
        timeout=10,
    )

    if not response.ok:
        detail = response.text or response.reason
        raise SystemExit(f"Submission failed: {response.status_code} {detail}")


if __name__ == "__main__":
    main()
