import numpy as np


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
    M = np.zeros((G, A), dtype=np.uint8)
    
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


def compute_best_guess(candidates, M, all_guesses):

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
