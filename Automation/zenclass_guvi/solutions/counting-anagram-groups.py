import sys
from collections import defaultdict

def main():
    data = sys.stdin.read().strip().split()
    if not data:
        print(0)
        return
    
    # Determine if first token is N
    # Sample 1: "7\nrat art cat act dog god tar pat" -> first token is "7"
    # Sample 2: "cat dog tac god act" -> no leading N, all are strings
    # Sample 3: "edcba the bread" -> no leading N, all are strings
    
    # Check if first token is a valid integer and corresponds to a count
    # If it's an integer and (len(data) - 1) >= int(data[0]), treat as N
    # Otherwise treat all tokens as strings (N = len(data))
    
    first = data[0]
    if first.lstrip('-').isdigit():
        try:
            n = int(first)
            if n >= 0 and (len(data) - 1) >= n:
                strings = data[1:1+n]
                # If n == 0, no strings
                # Otherwise process strings
                if n == 0:
                    print(0)
                    return
                anagram_groups = defaultdict(list)
                for s in strings:
                    key = ''.join(sorted(s))
                    anagram_groups[key].append(s)
                count = 0
                for key, group in anagram_groups.items():
                    if len(group) > 1:
                        count += 1
                print(count)
                return
        except (ValueError, IndexError):
            pass
    
    # All tokens are strings
    strings = data
    if not strings:
        print(0)
        return
    
    anagram_groups = defaultdict(list)
    for s in strings:
        key = ''.join(sorted(s))
        anagram_groups[key].append(s)
    
    count = 0
    for key, group in anagram_groups.items():
        if len(group) > 1:
            count += 1
    
    print(count)

if __name__ == "__main__":
    main()
