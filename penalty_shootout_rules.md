# Penalty Shootout Game

Each discrete turn pairs every ordered pair of distinct players twice: once with player \(i\) acting as shooter against keeper \(j\), and once with roles reversed. An action is a direction \(d \in \{0,1,2\}\) representing {left, centre, right}. Players may specify a direction for each opponent individually or broadcast a default alignment using the `"*"` key.

## Canonical State

- The game server records the turn history as a sequence of rounds.
- In round \(t\), the state stores for every shooter \(i\) a mapping from opponent \(j\) to the chosen \(d_{i \to j, t}\).
- Strategies submit an action payload of the form
  \[
  \{\texttt{"shoot"}: M^{\text{shoot}},\ \texttt{"keep"}: M^{\text{keep}}\},
  \]
  where each mapping \(M\) associates opponent identifiers with \(\{0,1,2\}\).

## Scoring

- Let \(p^{S}_{d_i, d_j}\) denote the probability that shooter direction \(d_i\) succeeds against keeper direction \(d_j\), and \(p^{K}_{d_j, d_i}\) the probability that the keeper scores when roles reverse. The default configuration uses the matrices documented in `penalty_shootout.py`.
- If `randomize_outcomes` is `False` (the default for the pilot), rewards are the expected values:
  - Shooter \(i\) receives \(p^{S}_{d_i, d_j} \cdot \text{goal\_reward} + (1 - p^{K}_{d_j, d_i}) \cdot \text{save\_reward}\).
  - Keeper \(j\) receives \( (1 - p^{S}_{d_i, d_j}) \cdot \text{save\_reward} + p^{K}_{d_j, d_i} \cdot \text{goal\_reward}\).
- When `randomize_outcomes` is enabled, the same probabilities govern Bernoulli draws for each interaction; rewards become sums of realised outcomes instead of expectations.

## Timing and Submission

- A global turn is processed every \( \Delta \) minutes (configured on the server). All actions submitted since the previous turn are aggregated.
- Submissions must occur before the processing timestamp. Late submissions roll to the next turn.
- Authentication is handled via the GitHub fine-grained token; no player identifier is required in the payload.

