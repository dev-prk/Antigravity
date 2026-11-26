import sys

def main():
    data = sys.stdin.read().strip()
    if not data:
        return
    n = int(data)
    
    total = 0
    for i in range(1, n + 1):
        term = 0
        for j in range(i):
            term = term * 10 + n
        total += term
    
    print(total)

if __name__ == "__main__":
    main()
