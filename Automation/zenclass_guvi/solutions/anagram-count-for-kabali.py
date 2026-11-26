import sys
from collections import Counter

def main():
    data = sys.stdin.read().split()
    if not data:
        print(0)
        return
    
    n = int(data[0])
    strings = data[1:n+1]
    
    target = 'kabali'
    target_counter = Counter(target)
    
    count = 0
    for s in strings:
        if len(s) == len(target) and Counter(s) == target_counter:
            count += 1
    
    print(count)

if __name__ == "__main__":
    main()
