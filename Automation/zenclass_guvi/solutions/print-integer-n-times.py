import sys

def main():
    lines = sys.stdin.read().strip().split()
    if len(lines) == 0:
        return
    A = int(lines[0])
    N = int(lines[1])
    for _ in range(N):
        print(A)

if __name__ == "__main__":
    main()
