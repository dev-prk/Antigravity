import sys
from itertools import permutations

def main():
    # Read input and strip any whitespace
    s = sys.stdin.read().strip()
    
    # Generate all unique permutations of the digits
    perms = set(permutations(s))
    
    # Calculate the sum of all permutations
    total = 0
    for p in perms:
        # Join the permutation tuple into a string and convert to integer
        num = int(''.join(p))
        total += num
    
    # Print the result
    print(total)

if __name__ == "__main__":
    main()
