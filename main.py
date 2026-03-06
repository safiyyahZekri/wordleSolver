"""Wordle Solver - Interactive game that suggests optimal guesses using information theory.

This module implements an interactive Wordle solver that uses entropy-based heuristics to find
the optimal next guess at each step. It loads word lists and a pre-computed pattern matrix,
then iteratively narrows down the set of candidate answers based on user feedback.
"""

import json
import numpy as np
from utils import build_pattern_matrix, compute_best_guess, pattern_to_code

# Debug flag for development/testing. Set to False before submission.
DEBUG = False

# Load the complete dictionary of valid guessable words (~13,000 words)
with open("dictionary_5_letter.json", "r") as f:
    all_guesses = json.load(f)

# Load the set of possible target words (~2,309 words)
with open("targets_5_letter.json", "r") as f:
    all_targets = json.load(f)



# Load or build the pattern matrix M
# M[i,j] = feedback code when guess i is tested against target j
# Shape: (len(all_guesses), len(all_targets))
try:
    M = np.load("pattern_matrix.npy")
except FileNotFoundError:
    print("Building pattern matrix (this may take a minute)...")
    M = build_pattern_matrix(all_guesses, all_targets)
    np.save("pattern_matrix.npy", M)


# Initialize game state
# candidates: indices of target words that are still possible solutions
# valid_guesses: set of words allowed as guesses
candidates = list(range(len(all_targets)))
valid_guesses = set(all_guesses)

# Main game loop: continue guessing until only one candidate remains
while len(candidates) > 1:
    # Find the guess that maximizes information gain (entropy reduction)
    best_word = compute_best_guess(candidates, M, all_guesses, all_targets)
    print(f"BEST={best_word}")

    # Get user's guess with validation
    while True:
        if DEBUG:
            print("Enter your guess:")
        guess = input().strip().lower()

        # Validate guess format and dictionary membership
        if len(guess) != 5:
            print("Guess must be exactly 5 letters.")
        elif not guess.isalpha():
            print("Guess must contain only letters.")
        elif guess not in valid_guesses:
            print("Word not in dictionary. Try again.")
        else:
            break  

    # Get user's feedback (r=red/wrong, y=yellow/wrong position, g=green/correct)
    while True:
        if DEBUG:
            print("Enter feedback (r/y/g):")
        feedback = input().strip().lower()

        # Validate feedback format
        if len(feedback) != 5:
            print("Feedback must be exactly 5 characters.")
        elif not all(c in 'ryg' for c in feedback):
            print("Feedback must only contain r, y, or g.")
        else:
            break  

    # Convert feedback string to numeric code
    code = pattern_to_code(feedback)

    # Filter candidates: only keep targets that would produce the same feedback
    guess_idx = all_guesses.index(guess)
    candidates = [c for c in candidates if M[guess_idx, c] == code]
    
    if len(candidates) == 0:
        print("No candidates remaining. The feedback might be incorrect.")
        break


# Output final answer when exactly one candidate remains, or error message
if len(candidates) == 1:
    print(f"BEST={all_targets[candidates[0]]}")
else:
    print("Could not determine the answer.")

