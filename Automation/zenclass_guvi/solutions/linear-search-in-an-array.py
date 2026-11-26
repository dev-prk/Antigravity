import sys

def main():
    data = sys.stdin.read().strip().splitlines()
    n = int(data[0])
    arr = list(map(int, data[1].split()))
    k = int(data[2])
    for i, val in enumerate(arr):
        if val == k:
            print(f"Element Found at Index: {i}")
            return
    print(-1)

if __name__ == "__main__":
    main()
