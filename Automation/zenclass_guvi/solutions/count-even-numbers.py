import sys

def main():
    data = sys.stdin.read().split()
    if not data:
        print(0)
        return
    n = int(data[0])
    count = 0
    for i in range(1, min(n, len(data) - 1) + 1):
        if int(data[i]) % 2 == 0:
            count += 1
    print(count)

if __name__ == "__main__":
    main()
