# Neutral Player Template

Starter package for building a penalty-shootout bot without any hard-coded identity.

## 1. Repository Setup

- **Fork vs clone:** use a **fork** if you intend to rely on GitHub Actions (recommended). A fork keeps the workflow file intact, lets you manage secrets per copy, and requires no extra remotes. A plain clone is fine for local iteration, but you must push to a repository you control before scheduled runs will work.
- **Create repository secrets and variables** under *Settings → Secrets and variables → Actions* for the repo that will host the bot:
  - Secrets:
    - `GAME_TOKEN` – fine-grained personal access token (PAT) scoped to this repository only. Enable the `Actions → Read and write` and `Workflows → Read and write` permissions. No other scopes are required.
    - `SERVER_URL` – base URL of the UBX server, e.g. `https://game-platform-v2-914970891924.us-central1.run.app`. Avoid pasting paths (like `/register`) onto the end; the scripts append those automatically.
  - Variables (optional):
    - `ENABLE_SCHEDULE` – set to `true` to let the cron job run. Leave unset or `false` to keep the workflow dormant unless you trigger it manually.

## 2. Registration

1. Choose an unused player handle (all lowercase, no spaces recommended).
2. Run `register.py` locally or via GitHub Actions:
   ```bash
   export SERVER_URL="https://game-platform-v2-914970891924.us-central1.run.app"
   export GITHUB_TOKEN="ghp_...."        # same PAT you stored as GAME_TOKEN
   export PLAYER_NAME="your-handle"
   python register.py
   ```
   You can also pass the player name as the first CLI argument instead of `PLAYER_NAME`.
3. The script echoes whether the player was newly registered or already present and prints the server-assigned player ID. No further configuration is required inside `strategy.py`; the API resolves the player via the token.
4. Troubleshooting tips:
   - If you see `SERVER_URL env var required`, double-check the secret or local export.
   - If you hit `Invalid URL '/register'`, it means the URL was missing a scheme (`https://`) or was left blank.
   - A `404 {"detail":"Not Found"}` usually means the URL contained extra path segments. Use the `show_state.py` utility (below) to confirm the `/status` endpoint resolves correctly.

## 3. Strategy Execution

- `strategy.py` fetches `/status`, filters out your own player using the PAT owner name, builds random `"shoot"` and `"keep"` maps, and submits them via `/action`.
- Replace the logic inside `strategy()` with your own. The payload must keep the structure returned by the helper (`{"shoot": {...}, "keep": {...}}`) with directions in `{"0","1","2"}`.
- **State format (`/status` response excerpt):**
  ```json
  {
    "gameState": {
      "turn_id": 7,
      "state": [
        {
          "player-id-1": { "player-id-2": "2", "player-id-3": "0" },
          "player-id-2": { "player-id-1": "1", "player-id-3": "1" }
        }
      ]
    },
    "players": [
      {
        "player_id": "player-id-1",
        "player_name": "handle-1",
        "player_github": "github-user-1",
        "current_action": null,
        "reward_history": [1.5, 2.0]
      }
    ]
  }
  ```
  - `gameState.state` is a list of rounds; each round maps shooter IDs to target-direction mappings.
  - `players` lists metadata for every registered participant.
- **Action format (payload sent to `/action`):**
  ```json
  {
    "action": {
      "shoot": {
        "player-id-2": "2",
        "player-id-3": "0"
      },
      "keep": {
        "player-id-2": "1",
        "player-id-3": "1"
      }
    }
  }
  ```
  - Keys under `shoot`/`keep` are opponent IDs. Use `"*": direction` to broadcast a default.
  - Directions must be strings `"0"`, `"1"`, or `"2"`.

## 4. GitHub Actions Workflow

- `.github/workflows/schedule_strategy.yml` runs every 10 minutes (`cron: */10`) and is also exposed via **Actions → Run workflow** for ad-hoc submission.
- To start the schedule:
  1. Ensure `GAME_TOKEN` and `SERVER_URL` secrets are populated.
  2. Set repository variable `ENABLE_SCHEDULE` to `true`.
  3. The next cron tick will fetch dependencies, execute `strategy.py`, and post the action. Logs surface under the workflow run.
- To trigger manually, leave `ENABLE_SCHEDULE` undefined, open the workflow page, and hit **Run workflow**. The run succeeds even when the schedule toggle is off.

## 5. Local Iteration

- Install dependencies: `pip install -r requirements.txt` (only `requests` is needed; feel free to manage it however you like).
- Run `python strategy.py` with `SERVER_URL` and `GITHUB_TOKEN` exported to emulate the CI behaviour.
- Quick status check: run `python show_state.py` (optionally set `SERVER_URL`) to print the current `/status` payload and verify connectivity before pushing changes.

Keep this template under version control, customise the strategy, and you are ready for the pilot. No player name is embedded in the action path; the token alone authenticates each submission.
