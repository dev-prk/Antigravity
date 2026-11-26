import sys

def main():
    data = sys.stdin.read().strip().split()
    if not data:
        print(0)
        return
    
    N = int(data[0])
    K = int(data[1])
    
    if K == 0:
        print(0)
        return
    
    A = list(map(int, data[2:2+K]))
    
    crashes = 0
    seen_remainders = set()
    
    for a in A:
        remainder = a % N
        if remainder in seen_remainders:
            crashes += 1
        else:
            seen_remainders.add(remainder)
    
    print(crashes)

if __name__ == "__main__":
    main()
