"""Utility functions for Wordle solver.

This module provides functions to:
- Compute feedback codes (comparing guesses against targets)
- Convert between feedback patterns and numeric codes
- Build the pattern matrix that maps all guess-target pairs to feedback codes
- Compute the optimal next guess using entropy-based heuristics
"""

import numpy as np


def compute_feedback(guess, target):
    """Compute feedback code for a guess against a target word.
    
    Args:
        guess: The guessed word (5-letter string)
        target: The target word to match against (5-letter string)
    
    Returns:
        int: Feedback code where each position i contains feedback[i] * 3^i
              0 = red (letter not in target)
              1 = yellow (letter in target but wrong position)
              2 = green (letter in target at correct position)
    
    Algorithm:
    1. First pass: Mark all exact matches (greens) and exclude them from remaining letters
    2. Second pass: For non-green positions, check if letter exists in remaining pool
    3. Only mark yellow if the letter is available (handles duplicate letter logic)
    """
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
    """Convert a feedback pattern string to numeric code.
    
    Args:
        pattern_str: String of 5 characters from {r, y, g}
                     r = red (0), y = yellow (1), g = green (2)
    
    Returns:
        int: Encoded pattern as base-3 number where position i has value * 3^i
    """
    mapping = {'r': 0, 'y': 1, 'g': 2}
    code = 0
    for k in range(5):
        code += mapping[pattern_str[k]] * (3 ** k)
    
    return code

def code_to_pattern(code):
    """Convert a numeric feedback code back to pattern string.
    
    Args:
        code: Base-3 encoded feedback (reverse of pattern_to_code)
    
    Returns:
        str: Pattern string of 5 characters from {r, y, g}
    """
    reverse_mapping = {0: 'r', 1: 'y', 2: 'g'}
    pattern = ""
    for k in range(5):
        digit = code % 3          # Extract base-3 digit
        pattern += reverse_mapping[digit]
        code = code // 3          # Remove processed digit
        
    
    return pattern

def build_pattern_matrix(all_guesses, all_targets):
    """Build a matrix of feedback codes for all guess-target pairs.
    
    Args:
        all_guesses: List of all valid guessable words
        all_targets: List of all possible target words
    
    Returns:
        np.ndarray: Matrix M of shape (len(all_guesses), len(all_targets))
                    M[i,j] = feedback code when guess i is tested against target j
                    Each code is in range [0, 242] representing 5 positions with 3 states each.
    
    Algorithm:
    1. Vectorize word characters as ASCII codes for fast comparison
    2. For each guess, compute feedback for all targets simultaneously:
       - First pass: identify exact matches (greens)
       - Second pass: identify wrong-position matches (yellows) with proper duplicate handling
    3. Convert feedback arrays to base-3 codes for compact storage
    
    Optimization:
    - Uses NumPy vectorization to avoid Python loops over targets
    - Stores results as uint16 (sufficient since max code = 2*(3^5) = 486)
    - Shows progress every 1000 guesses
    """

    G = len(all_guesses)  # Number of possible guesses
    A = len(all_targets)  # Number of possible targets

    # Convert words to ASCII character codes for efficient vectorized operations
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
    """Find the optimal next guess using entropy-based information theory.
    
    Args:
        candidates: List of indices of remaining possible target words
        M: Pattern matrix from build_pattern_matrix
        all_guesses: List of all valid guessable words
        all_targets: List of all possible target words
    
    Returns:
        str: The word that maximizes information gain (reduces uncertainty most)
    
    Algorithm (Information-Theoretic):
    - Prior entropy: H(W) = log2(number of candidates)
    - For each candidate guess:
        * Compute the distribution of feedback patterns it would produce
        * Calculate feedback entropy: H(Y) = -sum(p * log2(p)) for each feedback code
        * Higher entropy = more balanced splits = more information
    - Select guess with maximum feedback entropy
    - Information gain = H(Y) (expected reduction in candidate pool)
    
    The algorithm assumes each remaining candidate has equal probability and finds
    the guess that, on average, splits the candidates most evenly.
    """

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
    
    # Print diagnostic information
    print(f"Remaining candidates: {num_candidates}")
    print(f"Prior entropy H(W): {prior_entropy:.4f} bits")
    print(f"Best guess feedback entropy H(Y): {best_entropy:.4f} bits")
    print(f"Expected posterior entropy H(W|Y): {posterior_entropy:.4f} bits")
    print(f"Information gain I(W;Y): {best_entropy:.4f} bits")
    
    return all_guesses[best_guess_idx]