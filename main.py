<<<<<<< HEAD
<<<<<<< HEAD
=======
"""Wordle Solver - Interactive game that suggests optimal guesses using information theory.

This module implements an interactive Wordle solver that uses entropy-based heuristics to find
the optimal next guess at each step. It loads word lists and a pre-computed pattern matrix,
then iteratively narrows down the set of candidate answers based on user feedback.
"""

>>>>>>> safversion
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
<<<<<<< HEAD
=======
    print("Building pattern matrix (this may take a minute)...")
>>>>>>> safversion
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

<<<<<<< HEAD
        # Validate guess format and whether its in the dictionary of valid guesses
=======
        # Validate guess format and dictionary membership
>>>>>>> safversion
        if len(guess) != 5:
            print("Guess must be exactly 5 letters.")
        elif not guess.isalpha():
            print("Guess must contain only letters.")
        elif guess not in valid_guesses:
            print("Word not in dictionary. Try again.")
        else:
            break  

<<<<<<< HEAD
    # Get user's feedback (r=gray/wrong, y=yellow/wrong position, g=green/correct)
=======
    # Get user's feedback (r=red/wrong, y=yellow/wrong position, g=green/correct)
>>>>>>> safversion
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

<<<<<<< HEAD
    # Convert feedback string to numeric code(powers of 3)
=======
    # Convert feedback string to numeric code
>>>>>>> safversion
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

<<<<<<< HEAD
=======
import json
import sys
import utils
with open('dictionary_5_letter.json', 'r') as file:
    valid_guesses = json.load(file)

with open('targets_5_letter.json', 'r') as file:
    possible_answers = json.load(file)

try:
    with open('pattern_matrix.json', 'r') as file:
        M = json.load(file)
except FileNotFoundError:
    print("Error: The file 'pattern_matrix.json' was NOT found")
    utils.pattern_mat(valid_guesses, possible_answers)
    with open('pattern_matrix.json', 'r') as file:
        M = json.load(file)
except json.JSONDecodeError:
    print("Error: Failed to decode JSON from the file 'pattern_matrix.json'. The file might be corrupted or empty.")


entropy = {}
G = len(valid_guesses)
A = len(possible_answers)
index_possible = list(range(A))

while(len(index_possible) > 1):
    

    for i in range(G):
        entropy[i] = utils.calc_entropy(i, index_possible, M)

        # Calculate percentage
        percent = (i + 1) / G * 100
    
        # Create progress bar
        bar_length = 30
        filled = int(bar_length * (i + 1) // G)
        bar = '█' * filled + '░' * (bar_length - filled)
    
        # Print with carriage return to overwrite
        print(f'\rProgress: |{bar}| {i+1}/{G} ({percent:.1f}%)', end='', file=sys.stdout)
    
        # Flush to ensure it displays immediately
        sys.stdout.flush()

    print()  

    entropy = dict(sorted(entropy.items(), key=lambda item:item[1], reverse=True))

    print ("   Guess \t Entropy")
    keys = list(entropy.keys())
    values = list(entropy.values())

    for i in range(20):
        print(f"{i+1:2d}:{valid_guesses[keys[i]]}\t{values[i]}")
    print(f"Best: {valid_guesses[keys[0]]}")
    guess = input("Type the entered word: ")
    guessed_pattern = input("Enter the colors: ")
    guessed_pattern = utils.pattern_str_to_int(guessed_pattern)

    index_possible = utils.comp_pattern(guessed_pattern, guess, index_possible, valid_guesses, M)
    if len(index_possible) == 0:
        print("No words match! Did you enter the pattern correctly?")
        break
    if len(index_possible) < 50:
        print(f"Remaining words: {[possible_answers[i] for i in index_possible]}")


print(f"The correct answer is: {possible_answers[index_possible[0]]}")

>>>>>>> refs/remotes/origin/main
=======
>>>>>>> safversion
