import json
import numpy as np
from utils import build_pattern_matrix, compute_best_guess, pattern_to_code

with open("dictionary_5_letter.json", "r") as f:
    all_guesses = json.load(f)  # list of ~13,000 strings

with open("targets_5_letter.json", "r") as f:
    all_targets = json.load(f)  # list of ~2,309 strings



try:
    M = np.load("pattern_matrix.npy")
except FileNotFoundError:
    M = build_pattern_matrix(all_guesses, all_targets)
    np.save("pattern_matrix.npy", M)


# Game loop
candidates = list(range(len(all_targets)))
valid_guesses = set(all_guesses)

while len(candidates) > 1:
    best_word = compute_best_guess(candidates, M, all_guesses, all_targets)
    print(f"BEST={best_word}")

    while True:
        guess = input("Enter your guess: ").strip().lower()

        if len(guess) != 5:
            print("Guess must be exactly 5 letters.")
        elif not guess.isalpha():
            print("Guess must contain only letters.")
        elif guess not in valid_guesses:
            print("Word not in dictionary. Try again.")
        else:
            break  

    # --- Validate feedback ---
    while True:
        feedback = input("Enter feedback (r/y/g): ").strip().lower()

        if len(feedback) != 5:
            print("Feedback must be exactly 5 characters.")
        elif not all(c in 'ryg' for c in feedback):
            print("Feedback must only contain r, y, or g.")
        else:
            break  

    code = pattern_to_code(feedback)

    guess_idx = all_guesses.index(guess)
    candidates = [c for c in candidates if M[guess_idx, c] == code]
    if len(candidates) == 0:
        print("No candidates remaining. The feedback might be incorrect.")
        break


if len(candidates) == 1:
    print(f"BEST={all_targets[candidates[0]]}")
else:
    print("Could not determine the answer.")