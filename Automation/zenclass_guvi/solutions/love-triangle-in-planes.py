import sys

def main():
    data = sys.stdin.read().split()
    if not data:
        return
    n = int(data[0])
    f = list(map(int, data[1:1+n]))
    
    # Check for any 3-cycle: i -> f[i] -> f[f[i]] -> i
    for i in range(n):
        a = i
        b = f[a] - 1
        c = f[b] - 1
        if c != a and f[c] - 1 == a:
            print("YES")
            return
    
    print("NO")

if __name__ == "__main__":
    main()
