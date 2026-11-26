import sys
from collections import Counter

def main():
    data = sys.stdin.read().splitlines()
    if not data:
        return
    
    first_line = data[0].split()
    n = int(first_line[0])
    q = int(first_line[1])
    
    strings = []
    for i in range(1, n + 1):
        strings.append(data[i].strip())
    
    count = Counter(strings)
    
    results = []
    for i in range(n + 1, n + 1 + q):
        query = data[i].strip()
        results.append(str(count.get(query, 0)))
    
    print('\n'.join(results))

if __name__ == "__main__":
    main()
