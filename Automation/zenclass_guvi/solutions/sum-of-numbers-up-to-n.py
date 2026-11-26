import sys

def main():
    line = sys.stdin.readline().strip()
    if not line:
        print(0)
        return
    try:
        N = int(line)
    except ValueError:
        print(-1)
        return
    
    if N < 0:
        print(0)
    else:
        print(N * (N + 1) // 2)

if __name__ == "__main__":
    main()
