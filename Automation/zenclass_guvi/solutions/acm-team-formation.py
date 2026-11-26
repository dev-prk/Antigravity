import sys

def main():
    data = sys.stdin.read().strip().split()
    if not data:
        print(0)
        return
    
    n = int(data[0])
    k = int(data[1])
    
    if n == 0 or len(data) < 2 + n:
        print(0)
        return
    
    participates = list(map(int, data[2:2+n]))
    
    available = [5 - x for x in participates]
    
    available.sort()
    
    teams = 0
    i = 0
    
    while i + 2 < n:
        if available[i] >= k and available[i+1] >= k and available[i+2] >= k:
            teams += 1
            i += 3
        else:
            i += 1
    
    print(teams)

if __name__ == "__main__":
    main()
