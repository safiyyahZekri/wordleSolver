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