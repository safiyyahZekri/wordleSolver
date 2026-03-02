import numpy as np


def compute_feedback(guess, target):
    result = [0, 0, 0, 0, 0]
    
    target_remaining = list(target)
    for k in range(5):
        if guess[k] == target[k]:
            result[k] = 2                    
            target_remaining[k] = None       
    
    for k in range(5):
        if result[k] == 2:
            continue                        
        
        if guess[k] in target_remaining:
            result[k] = 1                   
            idx = target_remaining.index(guess[k])
            target_remaining[idx] = None

    
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

#helping func
def code_to_pattern(code):
   
    reverse_mapping = {0: 'r', 1: 'y', 2: 'g'}
    pattern = ""
    for k in range(5):
        digit = code % 3          
        pattern += reverse_mapping[digit]
        code = code // 3           
        
    
    return pattern

def build_pattern_matrix(all_guesses, all_targets):

    G = len(all_guesses)
    A = len(all_targets)

    guess_arr = np.array([[ord(c) for c in word] for word in all_guesses], dtype=np.uint8)
    target_arr = np.array([[ord(c) for c in word] for word in all_targets], dtype=np.uint8)

    M = np.zeros((G, A), dtype=np.uint16)
    for i in range(G):
        greens = (guess_arr[i] == target_arr)  
        result = np.zeros((A, 5), dtype=np.uint8) 
        result[greens] = 2  


        guess_letters = guess_arr[i]  
        remaining = target_arr.copy()  
        remaining[greens] = 0  

        for k in range(5):
            if True:  
                not_green = ~greens[:, k]  
                matches = (remaining == guess_letters[k])  
                has_match = matches.any(axis=1)  

                yellow = not_green & has_match  # shape (A,)
                result[yellow, k] = 1

                
                for j in range(5):
                    can_consume = yellow & (remaining[:, j] == guess_letters[k])
                    remaining[can_consume, j] = 0
                    yellow = yellow & ~can_consume

        powers = np.array([1, 3, 9, 27, 81], dtype=np.uint8)
        M[i] = (result * powers).sum(axis=1)

        if i % 1000 == 0:
            print(f"Computing row {i}/{G}...")

    return M


def compute_best_guess(candidates, M, all_guesses, all_targets):

    num_candidates = len(candidates)
    prior_entropy = np.log2(num_candidates)
    
    best_entropy = -1          
    best_guess_idx = 0         
    
    # Try every possible guess
    for i in range(len(all_guesses)):

        patterns = M[i, candidates]
        counts = np.bincount(patterns, minlength=243)
        counts = counts[counts > 0]
        probs = counts / num_candidates
        entropy = -np.sum(probs * np.log2(probs))
        
        if entropy > best_entropy:
            best_entropy = entropy
            best_guess_idx = i
    
  
    posterior_entropy = prior_entropy - best_entropy
    
    print(f"Remaining candidates: {num_candidates}")
    print(f"Prior entropy H(W): {prior_entropy:.4f} bits")
    print(f"Best guess feedback entropy H(Y): {best_entropy:.4f} bits")
    print(f"Expected posterior entropy H(W|Y): {posterior_entropy:.4f} bits")
    print(f"Information gain I(W;Y): {best_entropy:.4f} bits")
    
    return all_guesses[best_guess_idx]