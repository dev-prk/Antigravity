import sys

def main():
    data = sys.stdin.read().split()
    if not data:
        return
    try:
        r = int(data[0])
    except ValueError:
        return
    if r <= 0:
        return

    end = 2 * r + 1
    for i in range(r):
        start = 2 * i + 1
        print("".join(str(x) for x in range(start, end, 2)))

if __name__ == "__main__":
    main()
