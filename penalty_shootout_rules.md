# Penalty Shootout Game Rule

Let N denote the finite set of active players. Server time evolves in discrete turns (t = 1, 2, …). During each turn the platform inspects every unordered pair {i, j} with i ≠ j. For the ordered realisation (i, j) we read the event as “player i shoots on player j”; the reverse ordering (j, i) is evaluated in the same turn.

## Action space

At the start of turn t each player i submits an action consisting of two maps:

- shoot map: opponents → {0, 1, 2}
- keep map: opponents → {0, 1, 2}

The labels 0, 1, 2 correspond respectively to left, centre, and right. Players may provide an explicit direction for every opponent or rely on a broadcast entry "*" to supply a fallback value for any opponent not listed. The server resolves the broadcast before play and applies the same convention to both shoot and keep maps.

## State tracked by the server

The server maintains a turn-by-turn log denoted $H(t) = \{h_1, \dots, h_t\}$. Each entry $h_r$ is a dictionary with two components:

- the key `_turnId` with value $r$
- one key per player identifier, each mapped to a record of that player’s directions and (if known) realised outcome for round $r$

For a player labelled $k$, the stored record is
\[
R_k(r) = \{ "shoot": S_k(r),\ "keep": K_k(r),\ "outcome": O_k(r) \}.
\]

- $S_k(r)$ assigns a direction (string "0", "1", or "2") to every opponent shot at by $k$ in round $r$.
- $K_k(r)$ assigns the keeper direction to every opponent who shot at $k$.
- $O_k(r)$ appears only after the duel has been resolved; it maps each opponent to a realised value `goal = 1` or `goal = 0`.

If outcome information is not yet available for a pairing, the `"outcome"` entry is omitted for that round.

## Match payoffs

Let $P$ be the $3 \times 3$ matrix of success probabilities. Row indices correspond to shooting directions and column indices to keeping directions. The matrix is strictly dominated on the diagonal, i.e.
\[
P[d, d] < P[u, v] \qquad \text{for every direction } d \text{ and all ordered pairs } (u,v) \text{ with } u \neq v.
\]

A duel in round $t$ between shooter $i$ and keeper $j$ unfolds in three steps:

1. After broadcast resolution the server reads the directions $S_i(r)[j]$ and $K_j(r)[i]$.
2. It draws a Bernoulli random variable with success probability $P[S_i(r)[j], K_j(r)[i]]$.
3. A success is registered as a goal for the shooter; a failure is recorded as a save for the keeper. The symmetric duel $(j,i)$ is evaluated in the same turn.