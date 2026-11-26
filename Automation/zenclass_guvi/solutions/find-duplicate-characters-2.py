import sys
from collections import Counter

def main():
    s = sys.stdin.readline().rstrip('\n')
    if not s:
        print(-1)
        return
    
    # Count all characters
    count = Counter(s)
    
    # Find characters that appear more than once
    duplicates = [char for char in count if count[char] > 1]
    
    if not duplicates:
        print(-1)
    else:
        print(''.join(duplicates))

if __name__ == "__main__":
    main()
