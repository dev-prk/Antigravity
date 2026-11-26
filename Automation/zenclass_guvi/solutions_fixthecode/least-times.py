from collections import Counter
import sys

def main():
    data = sys.stdin.read().strip().split()
    n = int(data[0])
    arr = list(map(int, data[1:n+1]))
    
    if n == 0:
        return
    
    count = Counter(arr)
    min_count = min(count.values())
    
    for num in arr:
        if count[num] == min_count:
            print(num)
            return

if __name__ == "__main__":
    main()
