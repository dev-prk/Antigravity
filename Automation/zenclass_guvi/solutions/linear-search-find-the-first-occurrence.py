import sys

def main():
    data = sys.stdin.read().split()
    if not data:
        return
    n = int(data[0])
    arr = list(map(int, data[1:1 + n]))
    target = int(data[1 + n])
    for i, val in enumerate(arr):
        if val == target:
            print(i)
            return
    print(-1)

if __name__ == "__main__":
    main()
