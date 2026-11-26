import sys

def main():
    data = sys.stdin.read().strip().split()
    if not data:
        return
    n = int(data[0])
    if n == 0:
        return
    numbers = list(map(int, data[1:n+1]))
    print(min(numbers))

if __name__ == "__main__":
    main()
