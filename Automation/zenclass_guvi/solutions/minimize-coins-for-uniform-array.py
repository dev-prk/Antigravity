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
    if len(arr) == 0:
        print(0)
        return
    
    total_sum = sum(arr)
    freq = Counter(arr)
    
    min_coins = float('inf')
    for target, count in freq.items():
        coins = total_sum - target * count
        if coins < min_coins:
            min_coins = coins
    
    print(min_coins)

if __name__ == "__main__":
    main()
