import sys

def main():
    data = sys.stdin.buffer.read().split()
    if len(data) < 2:
        print("no")
        return

    n = int(data[0])
    k = int(data[1])
    end = min(len(data), 2 + max(n, 0))

    for i in range(2, end):
        if int(data[i]) == k:
            print("yes")
            return

    print("no")

if __name__ == "__main__":
    main()
