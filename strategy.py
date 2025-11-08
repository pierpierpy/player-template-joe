#!/usr/bin/env python3
import os
from typing import Any, Dict, List, Tuple

import numpy as np
import requests


PLAYER_NAME = os.getenv("PLAYER_NAME", "player-template").strip()
SERVER_URL = os.getenv("SERVER_URL")
GITHUB_TOKEN = os.getenv("GITHUB_TOKEN")


def strategy(state: Dict[str, Any]) -> Dict[str, Dict[str, int]]:
    opponents = _resolve_opponents(state, PLAYER_NAME)
    if not opponents:
        raise SystemExit("No opponents found in game state; cannot build payload.")

    shoot_dirs = np.random.randint(0, 3, len(opponents)).tolist()
    keep_dirs = np.random.randint(0, 3, len(opponents)).tolist()

    return {
        "shoot": {pid: int(direction) for pid, direction in zip(opponents, shoot_dirs)},
        "keep": {pid: int(direction) for pid, direction in zip(opponents, keep_dirs)},
    }


def _resolve_opponents(state: Dict[str, Any], player_name: str) -> List[str]:
    participants: set[str] = set()

    for name in state.get("playerNames") or []:
        if name:
            participants.add(str(name))

    for round_entry in state.get("state") or []:
        if not isinstance(round_entry, dict):
            continue
        for shooter, actions in round_entry.items():
            if shooter:
                participants.add(str(shooter))
            if isinstance(actions, dict):
                for role in ("shoot", "keep"):
                    for opponent in (actions.get(role) or {}).keys():
                        if opponent:
                            participants.add(str(opponent))

    if not participants:
        raise SystemExit("No players present in game state; cannot submit action.")

    self_name = player_name.strip()
    if self_name and self_name not in participants:
        raise SystemExit(f"Could not find player '{player_name}' in /status response.")

    return sorted(pid for pid in participants if pid != self_name)


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
