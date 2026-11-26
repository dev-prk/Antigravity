import sys

def main():
    data = sys.stdin.read().split()
    if not data:
        return
    
    n = int(data[0])
    if n <= 0:
        print()
        return
    
    vals = data[1:1 + n]
    idx = 1 + n
    k = int(data[idx]) if idx < len(data) else 0
    
    k = k % n
    rotated = vals[n - k:] + vals[:n - k]
    sys.stdout.write(' '.join(rotated) + '\n')

if __name__ == '__main__':
    main()
