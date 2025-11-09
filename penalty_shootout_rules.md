# Penalty Shootout Game Rule

Let N denote the finite set of active players. Server time evolves in discrete turns (t = 1, 2, …). During each turn the platform inspects every unordered pair {i, j} with i ≠ j. For the ordered realisation (i, j) we read the event as “player i shoots on player j”; the reverse ordering (j, i) is evaluated in the same turn.

## Action space

At the start of turn t each player i submits an action consisting of two maps:

- shoot map: opponents → {0, 1, 2}
- keep map: opponents → {0, 1, 2}

The labels 0, 1, 2 correspond respectively to left, centre, and right. Players may provide an explicit direction for every opponent or rely on a broadcast entry "*" to supply a fallback value for any opponent not listed. The server resolves the broadcast before play and applies the same convention to both shoot and keep maps.

## State tracked by the server

The public state is a history H(t) = {h₁, …, h_t}. Each round record h_r contains:

- the turn identifier `_turnId = r`
- for every player k, the maps `shoot_k(r)` and `keep_k(r)` recorded as strings "0", "1", "2"
- when outcomes have been realised, an additional map `outcome_k(r)` indicating, for each opponent, whether the shot against or by that opponent resulted in a goal (1) or a save (0)

If the outcome information is not yet available, the field is omitted for that round.

## Payoff mechanism

Let P be the 3 × 3 success-probability matrix whose rows index shooting directions and columns index keeping directions. The matrix satisfies the dominance property `P[d, d] < P[u, v]` for every direction d and any ordered pair (u, v) with u ≠ v. Intuitively, a shot aimed away from the keeper’s chosen direction strictly improves the conversion probability relative to a shot that matches it.

During round t, a duel involving shooter i and keeper j proceeds as follows:

1. The server reads the directions `a = shoot_i(j)` and `b = keep_j(i)` after broadcast resolution.
2. A Bernoulli random draw succeeds with probability `P[a, b]`.
3. Success is recorded as a goal for i; failure is recorded as a save for j.
4. Payoffs are realised outcomes: the shooter receives `R_goal` for a goal, the keeper receives `R_save` for a save. Default values satisfy `R_goal = R_save = 1`, with alternative parameters accepted via the environment variables `PENALTY_GOAL_REWARD` and `PENALTY_SAVE_REWARD`.

The same procedure is applied to the symmetric event (j, i) within the turn. Continuous play arises because the scheduler triggers strategy submissions at a fixed cadence.