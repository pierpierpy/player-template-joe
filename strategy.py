#!/usr/bin/env python3
import os
from typing import Any, Dict, List

import numpy as np
import requests


def strategy(state: Dict[str, Any]) -> Dict[str, Dict[str, str]]:
    players = state.get("players") or []

    opponents = [
        str(player.get("player_id") or player.get("playerId"))
        for player in players
        if player.get("player_id") or player.get("playerId")
    ]

    if not opponents:
        direction = str(np.random.randint(0, 3))
        return {"shoot": {"*": direction}, "keep": {"*": direction}}

    shoot_dirs = np.random.randint(0, 3, len(opponents))
    keep_dirs = np.random.randint(0, 3, len(opponents))

    return {
        "shoot": {pid: str(direction) for pid, direction in zip(opponents, shoot_dirs)},
        "keep": {pid: str(direction) for pid, direction in zip(opponents, keep_dirs)},
    }


SERVER_URL = os.getenv("SERVER_URL")
GITHUB_TOKEN = os.getenv("GITHUB_TOKEN")


def main() -> None:
    if not SERVER_URL:
        raise SystemExit("SERVER_URL env var required")

    status = requests.get(f"{SERVER_URL}/status", timeout=10)
    status.raise_for_status()
    payload = status.json()
    action = strategy(payload)

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
