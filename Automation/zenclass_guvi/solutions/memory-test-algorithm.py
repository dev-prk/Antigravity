import sys
from collections import Counter

def main():
    data = sys.stdin.read().split()
    idx = 0
    if idx >= len(data):
        return
    
    # First number is N (size of array)
    n = int(data[idx]); idx += 1
    arr = []
    for i in range(n):
        if idx >= len(data):
            break
        arr.append(int(data[idx])); idx += 1
    
    if idx >= len(data):
        return
    t = int(data[idx]); idx += 1
    queries = []
    for i in range(t):
        if idx >= len(data):
            break
        queries.append(int(data[idx])); idx += 1
    
    freq = Counter(arr)
    results = []
    for q in queries:
        if q in freq:
            results.append(str(freq[q]))
        else:
            results.append("Not Present")
    print(" ".join(results))

if __name__ == "__main__":
    main()
