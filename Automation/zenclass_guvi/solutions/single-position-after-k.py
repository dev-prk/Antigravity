import sys
import re

def main():
    line = sys.stdin.readline().strip()
    
    # Extract p part: "p=[2,3,1]"
    p_match = re.search(r'p=\[([^\]]+)\]', line)
    p_str = p_match.group(1)
    p = list(map(int, p_str.split(',')))
    
    # Extract i and k using regex
    i_match = re.search(r'i=(\d+)', line)
    k_match = re.search(r'k=(\d+)', line)
    
    i = int(i_match.group(1))
    k = int(k_match.group(1))
    
    # Convert to 0-indexed
    current = i - 1
    
    for _ in range(k):
        current = p[current] - 1
    
    # Convert back to 1-indexed
    print(current + 1)

if __name__ == "__main__":
    main()
