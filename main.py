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

