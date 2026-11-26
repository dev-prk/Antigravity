import sys
from collections import Counter

def main():
    data = sys.stdin.read().strip().split()
    if not data:
        print(0)
        return
    
    n = int(data[0])
    if n == 0:
        print(0)
        return
    
    arr = list(map(int, data[1:n+1]))
    
    if n <= 1:
        print(0)
        return
    
    freq = Counter(arr)
    
    count = 0
    for i in range(n - 1):
        if freq[arr[i]] == arr[i + 1]:
            count += 1
    
    print(count)

if __name__ == "__main__":
    main()
