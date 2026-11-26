import sys
from collections import Counter

def main():
    data = sys.stdin.read().strip().split()
    if not data:
        return
    n = int(data[0])
    # Take exactly n numbers after the first token
    numbers = list(map(int, data[1:1 + n]))
    
    freq = Counter(numbers)
    repeated = [num for num, count in freq.items() if count > 1]
    
    if not repeated:
        print("unique")
    else:
        repeated.sort()
        print(' '.join(map(str, repeated)))

if __name__ == "__main__":
    main()
