#!/usr/bin/env python3
import os
import random
from typing import Any, Dict, List

import requests


PLAYER_NAME = os.getenv("PLAYER_NAME", "panenka-template")
SERVER_URL = os.getenv("SERVER_URL")
GITHUB_TOKEN = os.getenv("GITHUB_TOKEN")

if not SERVER_URL:
    raise SystemExit("SERVER_URL env var required")


def random_direction() -> str:
    return random.choice(["0", "1", "2"])


def extract_opponents(status: Dict[str, Any], self_name: str) -> List[str]:
    players = status.get("players") or []
    opponent_names: List[str] = []
    for player in players:
        name = player.get("playerName") or player.get("player_name")
        if not name or name == self_name:
            continue
        opponent_names.append(name)
    return opponent_names


def build_action(status: Dict[str, Any], self_name: str) -> Dict[str, Dict[str, str]]:
    opponent_names = extract_opponents(status, self_name)
    shoot_map: Dict[str, str] = {name: random_direction() for name in opponent_names}
    keep_map: Dict[str, str] = {name: random_direction() for name in opponent_names}
    if not shoot_map:
        direction = random_direction()
        shoot_map["*"] = direction
        keep_map["*"] = direction
    return {"shoot": shoot_map, "keep": keep_map}


def main() -> None:
    status_response = requests.get(f"{SERVER_URL}/status", timeout=10)
    status_response.raise_for_status()
    status = status_response.json()

    action = build_action(status, PLAYER_NAME or "")

    headers = {"Content-Type": "application/json"}
    if GITHUB_TOKEN:
        headers["Authorization"] = f"Bearer {GITHUB_TOKEN}"

    payload = {"action": action}
    if PLAYER_NAME:
        payload["player_name"] = PLAYER_NAME

    requests.post(
        f"{SERVER_URL}/action",
        headers=headers,
        json=payload,
        timeout=10,
    ).raise_for_status()


if __name__ == "__main__":
    main()