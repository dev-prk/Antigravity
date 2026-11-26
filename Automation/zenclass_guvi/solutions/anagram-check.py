import sys
from collections import Counter

def main():
    # Read two lines from stdin
    s1 = sys.stdin.readline().rstrip('\n')
    s2 = sys.stdin.readline().rstrip('\n')
    
    # Check if they are anagrams
    if Counter(s1) == Counter(s2):
        print(1)
    else:
        print(0)

if __name__ == "__main__":
    main()
