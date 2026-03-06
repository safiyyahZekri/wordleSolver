<<<<<<< HEAD
import numpy as np


def compute_feedback(guess, target):
    result = [0, 0, 0, 0, 0]
    
    # First pass: identify exact matches (green feedback)
    target_remaining = list(target)
    for k in range(5):
        if guess[k] == target[k]:
            result[k] = 2                    # Green: exact match
            target_remaining[k] = None       # Mark as consumed
    
    # Second pass: identify wrong-position matches (yellow feedback)
    for k in range(5):
        if result[k] == 2:
            continue                        # Skip positions already marked green
        
        # Check if guessed letter exists in remaining target letters
        if guess[k] in target_remaining:
            result[k] = 1                   # Yellow: letter in target but wrong position
            idx = target_remaining.index(guess[k])
            target_remaining[idx] = None    # Mark as consumed

    # Convert result array to base-3 code for compact storage
    code = 0
    for k in range(5):
        code += result[k] * (3 ** k)
         
    
    return code

def pattern_to_code(pattern_str):
    mapping = {'r': 0, 'y': 1, 'g': 2}
    code = 0
    for k in range(5):
        code += mapping[pattern_str[k]] * (3 ** k)
    
    return code

#helping func (for debugging)
def code_to_pattern(code):
   
    reverse_mapping = {0: 'r', 1: 'y', 2: 'g'}
    pattern = ""
    for k in range(5):
        digit = code % 3          # Extract base-3 digit
        pattern += reverse_mapping[digit]
        code = code // 3          # Remove processed digit
        
    
    return pattern

def build_pattern_matrix(all_guesses, all_targets):

    G = len(all_guesses)
    A = len(all_targets)

    guess_arr = np.array([[ord(c) for c in word] for word in all_guesses], dtype=np.uint8)
    target_arr = np.array([[ord(c) for c in word] for word in all_targets], dtype=np.uint8)

    # Output matrix: M[i,j] will contain feedback code for guess i vs target j
    M = np.zeros((G, A), dtype=np.uint16)
    
    for i in range(G):
        # First pass: identify all exact matches (green feedback = 2)
        greens = (guess_arr[i] == target_arr)  # Boolean array: (A, 5)
        result = np.zeros((A, 5), dtype=np.uint8) 
        result[greens] = 2  # Mark all greens

        # Prepare for second pass: track which letters remain available in each target
        guess_letters = guess_arr[i]  # Shape: (5,)
        remaining = target_arr.copy()  # Shape: (A, 5) - copy to avoid modifying original
        remaining[greens] = 0  # Consume letters that were matched as green

        # Second pass: identify wrong-position matches (yellow feedback = 1)
        for k in range(5):
            # For each position k in the guess
            not_green = ~greens[:, k]  # Positions in targets that aren't green at position k
            matches = (remaining == guess_letters[k])  # Where the guess letter appears in remaining
            has_match = matches.any(axis=1)  # Which targets have this letter somewhere

            yellow = not_green & has_match  # Positions that are yellow (not green but letter exists)
            result[yellow, k] = 1  # Mark as yellow

            # Consume the matched letter from remaining (handle duplicates properly)
            for j in range(5):
                can_consume = yellow & (remaining[:, j] == guess_letters[k])
                remaining[can_consume, j] = 0  # Mark letter as consumed
                yellow = yellow & ~can_consume  # Only consume once per yellow position

        # Convert feedback array to base-3 encoding
        powers = np.array([1, 3, 9, 27, 81], dtype=np.uint8)
        M[i] = (result * powers).sum(axis=1)

        if i % 1000 == 0:
            print(f"Computing row {i}/{G}...")

    return M


def compute_best_guess(candidates, M, all_guesses, all_targets):

    num_candidates = len(candidates)
    prior_entropy = np.log2(num_candidates)  # H(W): uncertainty in answer
    
    best_entropy = -1          # Track best entropy found so far
    best_guess_idx = 0         # Index of best guess
    
    # Try every possible guess word and evaluate how informative it would be
    for i in range(len(all_guesses)):
        # Get feedback patterns for this guess against all remaining candidates
        patterns = M[i, candidates]
        
        # Count how many times each feedback pattern appears
        counts = np.bincount(patterns, minlength=243)  # 3^5 = 243 possible codes
        counts = counts[counts > 0]  # Only keep counts that are non-zero
        
        # Convert counts to probabilities
        probs = counts / num_candidates
        
        # Calculate entropy of the feedback distribution: H(Y)
        # High entropy = feedback splits candidates evenly = good guess
        entropy = -np.sum(probs * np.log2(probs))
        
        # Keep track of the guess with highest entropy
        if entropy > best_entropy:
            best_entropy = entropy
            best_guess_idx = i
    
    # Calculate expected entropy after receiving feedback
    posterior_entropy = prior_entropy - best_entropy
    
    print(f"Remaining candidates: {num_candidates}")
    print(f"Prior entropy H(W): {prior_entropy:.4f} bits")
    print(f"Best guess feedback entropy H(Y): {best_entropy:.4f} bits")
    print(f"Expected posterior entropy H(W|Y): {posterior_entropy:.4f} bits")
    print(f"Information gain I(W;Y): {best_entropy:.4f} bits")
    
    return all_guesses[best_guess_idx]
=======
import json 
import sys
import math
import numpy as np
from multiprocessing import Pool
import os
import time

def pattern_mat(valid_guesses, possible_answers):
    filename='pattern_matrix.json'
    G = len(valid_guesses)
    A = len(possible_answers)
    W = 5
    start = time.time()
    for target in possible_answers:
        get_pattern(valid_guesses[0], target)
    elapsed = time.time() - start

    print(f"One row took: {elapsed:.3f} seconds")
    patterns = [[0]*A for _ in range(G)]
    
    print("Making the Pattern Matrix...")
    for i, guess in enumerate(valid_guesses):
        for j, target in enumerate(possible_answers):
            patterns[i][j] = get_pattern(guess, target)

            percent = ((i*A+j+1) / (G*A))*100
            current = i * A + j + 1

            print(f'\rProgress: {current}/{G*A}({percent:.1f}%)', end='', file=sys.stdout)
            sys.stdout.flush()

    with open(filename, 'w') as json_file:
        json.dump(patterns, json_file, indent=4)
    print("\nPattern Matrix Done.")

def get_pattern(guess, target):
    target_chars = list(target)
    pattern = 0

    green_mark = [False]*5
    for i in range(5):
        if guess[i] == target[i]:
            pattern+= 2 * 3**i
            target_chars[i] = None
            green_mark[i] = True
    for i in range(5):
        if not green_mark[i]:
            if guess[i] in target_chars:
                pattern+= 3**i
                """removing first occurrence 34an lama el guessed word has 
                   2 duplicate letters but the secret word has it only once 
                   yeb2a the first of the 2 is yellow(if it is in the wrong 
                   position) and the 2nd is grey """
                j = target_chars.index(guess[i])
                target_chars[j] = None
    return pattern

def comp_pattern(guessed_pattern, guess, index_possible, valid_guesses, M):
    g = valid_guesses.index(guess)
    return [i for i in index_possible if M[g][i] == guessed_pattern]

def calc_entropy(g, index_possible, M):
    pattern_groups = {}
    for i in index_possible:
        if M[g][i] in pattern_groups:
            pattern_groups[M[g][i]] += 1
        else :
            pattern_groups[M[g][i]] = 1
    
    total = len(index_possible)
    entropy = 0

    for pattern, count in pattern_groups.items():
        prob = count / total
        entropy -= prob * math.log2(prob)
    return entropy

def pattern_str_to_int(guessed_pattern):
    guessed_pattern = list(guessed_pattern)
    pattern = 0
    for i, char in enumerate(guessed_pattern):
        if char == 'g':
            pattern += 2 * 3**i
        elif char == 'y':
            pattern += 3**i
            
    return pattern





# Test function
def test_pattern_conversion():
    test_cases = [
        ("soare", "soare", "ggggg"),  # Should be all greens
        ("soare", "house", "bybyg"),  # Example pattern
    ]
    
    for guess, target, expected_str in test_cases:
        code = get_pattern(guess, target)
        # Convert back to string to verify
        back_to_str = ""
        temp = code
        for i in range(5):
            digit = (temp // (3**i)) % 3
            if digit == 2:
                back_to_str = 'g' + back_to_str
            elif digit == 1:
                back_to_str = 'y' + back_to_str
            else:
                back_to_str = 'b' + back_to_str
        
        print(f"{guess} vs {target}: code={code}, expected={expected_str}, got={back_to_str}")
        assert back_to_str == expected_str, f"Mismatch: {back_to_str} vs {expected_str}"
>>>>>>> refs/remotes/origin/main
