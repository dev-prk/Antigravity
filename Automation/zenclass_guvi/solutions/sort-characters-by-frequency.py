from collections import Counter
import sys

def main():
    s = sys.stdin.readline().strip()
    
    if not s:
        print("")
        return
    
    freq = Counter(s)
    
    sorted_chars = sorted(freq.keys(), key=lambda x: (-freq[x], x))
    
    result = ''.join(char * freq[char] for char in sorted_chars)
    print(result)

if __name__ == "__main__":
    main()
