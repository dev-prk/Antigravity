import sys
from itertools import combinations

def main():
    s = sys.stdin.readline().strip()
    
    if len(s) < 3:
        print(0)
        return
    
    # Generate all combinations of 3 characters
    combs = list(combinations(s, 3))
    
    # Sort lexicographically
    combs.sort()
    
    # Print results
    print(len(combs))
    for c in combs:
        print(''.join(c))

if __name__ == "__main__":
    main()
