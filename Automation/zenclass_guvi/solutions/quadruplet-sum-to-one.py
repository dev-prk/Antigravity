import sys
from itertools import combinations

def main():
    data = sys.stdin.read().strip().split()
    n = int(data[0])
    numbers = list(map(int, data[1:1+n]))
    
    found = False
    for quad in combinations(numbers, 4):
        if sum(quad) == 1:
            found = True
            break
    
    print("Yes" if found else "No")

if __name__ == "__main__":
    main()
