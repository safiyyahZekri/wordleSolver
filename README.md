# Wordle Solver

An optimal Wordle solver that uses **information theory** to recommend the best guess at every step. It works by choosing the word whose feedback pattern maximizes **Shannon entropy** — effectively splitting the remaining candidates as evenly as possible with each guess.

## How It Works

The solver models Wordle as an information-theoretic problem. Before any guess, the uncertainty about the hidden word is `log₂(N)` bits, where `N` is the number of remaining candidates. Each guess produces a colored feedback pattern (green, yellow, gray) that eliminates some candidates. The best guess is the one whose feedback distribution has the highest entropy, meaning it extracts the most information on average regardless of what the hidden word turns out to be.

**Key steps:**

1. **Precompute a pattern matrix** — For every possible guess–target pair, the solver calculates what feedback pattern would result and stores it as a compact base-3 code. This matrix (`12,970 guesses × 3,242 targets`) is built once and cached to disk as `pattern_matrix.npy`.
2. **Rank guesses by entropy** — At each turn, the solver evaluates every guess word against the current candidate set, counts how the feedback patterns are distributed, and picks the guess with the highest Shannon entropy.
3. **Filter candidates** — After the user enters their guess and the feedback they received, the solver discards any candidate that wouldn't produce that exact feedback, narrowing the search.
4. **Repeat** until only one candidate remains.

## Project Structure

```
├── main.py                  # Game loop: recommends guesses, reads feedback, filters candidates
├── utils.py                 # Core algorithms: pattern computation, entropy ranking, matrix building
├── dictionary_5_letter.json # Full dictionary of valid guesses (12,970 words)
├── targets_5_letter.json    # Possible target/answer words (3,242 words)
└── pattern_matrix.npy       # Precomputed feedback matrix (generated on first run)
```

## Requirements

- Python 3.8+
- NumPy

```bash
pip install numpy
```

## Usage

Run the solver and follow its prompts:

```bash
python main.py
```

Each round, the solver will:

1. Print `BEST=<word>` — its recommended guess.
2. Wait for you to type the **guess** you actually played (must be a valid 5-letter word from the dictionary).
3. Wait for you to type the **feedback** you received as a 5-character string using `r` (gray), `y` (yellow), and `g` (green).

**Example session:**

```
BEST=salet
> salet
> rygry
BEST=corni
> corni
> grgrg
BEST=condi
```

The first run will take a few minutes to build `pattern_matrix.npy`. Subsequent runs load it instantly.

## Feedback Encoding

| Character | Color  | Meaning                        |
|-----------|--------|--------------------------------|
| `r`       | Gray   | Letter is not in the target    |
| `y`       | Yellow | Letter is in the target but in the wrong position |
| `g`       | Green  | Letter is in the correct position |

## Configuration

Set `DEBUG = True` in `main.py` to enable input prompts (helpful when running interactively in a terminal). When `DEBUG = False`, the solver suppresses prompt text so it can be driven programmatically via stdin/stdout.

## Performance

The entropy-based strategy typically solves Wordle in **3–4 guesses**. Because it searches the full 12,970-word guess space (not just possible answers), it can find highly informative opening words that wouldn't otherwise be considered.

## How the Math Works

The solver treats each guess as a random variable whose outcome is the feedback pattern. For a guess `g` and candidate set `C`:

- Each feedback pattern `p` has probability `P(p) = |{w ∈ C : feedback(g, w) = p}| / |C|`
- The entropy of guess `g` is `H(g) = −Σ P(p) log₂ P(p)`
- The solver picks `g* = argmax H(g)` over all valid guesses

Higher entropy means the feedback is more uniformly distributed across patterns, so on average each outcome eliminates more candidates.


### project by:
JanaBialy + SafiyyahZekri
