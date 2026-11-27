import sys

def main():
    data = sys.stdin.read().split()
    t = int(data[0])
    idx = 1
    results = []
    
    for _ in range(t):
        n = int(data[idx])
        x = int(data[idx + 1])
        idx += 2
        a = list(map(int, data[idx:idx + n]))
        idx += n
        
        a.sort(reverse=True)
        count = 0
        total = 0
        
        for i in range(n):
            total += a[i]
            if total // (i + 1) >= x:
                count = i + 1
        
        results.append(count)
    
    for r in results:
        print(r)

if __name__ == "__main__":
    main()
