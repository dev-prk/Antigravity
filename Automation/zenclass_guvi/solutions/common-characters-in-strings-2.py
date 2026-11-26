import sys

def main():
    data = sys.stdin.read().splitlines()
    s1 = data[0] if len(data) > 0 else ""
    s2 = data[1] if len(data) > 1 else ""
    
    # Build frequency map for characters in s1
    freq = {}
    for char in s1:
        freq[char] = freq.get(char, 0) + 1
    
    # Find common characters in order of appearance in s1
    result = []
    for char in s2:
        if freq.get(char, 0) > 0:
            result.append(char)
            freq[char] -= 1
    
    if not result:
        print(-1)
    else:
        print(''.join(result))

if __name__ == "__main__":
    main()
