import sys

def main():
    data = sys.stdin.read().strip().split()
    if not data:
        print(-1)
        return
    
    A, B, C = map(int, data[:3])
    
    # Handle edge cases
    if C <= 0:
        print(-1)
        return
    
    # Sum of arithmetic series: S = n/2 * (2a + (n-1)d)
    # where a = A, d = B, n = C
    result = C * (2 * A + (C - 1) * B) // 2
    print(result)

if __name__ == "__main__":
    main()
