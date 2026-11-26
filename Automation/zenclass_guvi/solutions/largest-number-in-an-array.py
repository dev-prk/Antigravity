import sys

def main():
    data = sys.stdin.read().strip().split()
    if not data:
        print(-1)
        return
    n = int(data[0])
    if n == 0:
        print(-1)
        return
    numbers = list(map(int, data[1:n+1]))
    if not numbers:
        print(-1)
        return
    print(max(numbers))

if __name__ == "__main__":
    main()
