import sys

def main():
    data = sys.stdin.read().strip().split()
    if not data:
        return
    
    n = int(data[0])
    
    if n == 0:
        print("")
        return
    
    a = list(map(int, data[1:1+n]))
    b = list(map(int, data[1+n:1+2*n]))
    
    c = []
    for i in range(n):
        c.append(str(a[i] + b[i]))
    
    print(' '.join(c))

if __name__ == "__main__":
    main()
