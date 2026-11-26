import sys

def main():
    data = sys.stdin.buffer.read().split()
    if not data:
        return
    n = int(data[0])
    if n <= 0:
        print(0)
        return
    if len(data) < 2:
        print(0)
        return
    mn = mx = int(data[1])
    limit = min(len(data), n + 1)
    for i in range(2, limit):
        x = int(data[i])
        if x < mn:
            mn = x
        if x > mx:
            mx = x
    print(mx - mn)

if __name__ == "__main__":
    main()
