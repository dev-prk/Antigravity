import sys

def main():
    data = sys.stdin.read().strip().split()
    if not data:
        print(0)
        return
    n = int(data[0])
    if n == 0:
        print(0)
        return
    arr = list(map(int, data[1:n+1]))
    if n == 1:
        print(0)
        return
    min_val = min(arr)
    max_val = max(arr)
    print(abs(max_val - min_val))

if __name__ == "__main__":
    main()
