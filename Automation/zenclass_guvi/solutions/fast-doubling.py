import sys

def fibonacci(n):
    if n == 0:
        return 0
    if n == 1:
        return 1
    
    def fast_doubling(k):
        if k == 0:
            return (0, 1)
        a, b = fast_doubling(k // 2)
        c = a * (2 * b - a)
        d = a * a + b * b
        
        if k % 2 == 0:
            return (c, d)
        else:
            return (d, c + d)
    
    return fast_doubling(n)[0]

def main():
    line = sys.stdin.readline().strip()
    if '=' in line:
        n = int(line.split('=')[1])
    else:
        n = int(line)
    print(fibonacci(n))

if __name__ == "__main__":
    main()
