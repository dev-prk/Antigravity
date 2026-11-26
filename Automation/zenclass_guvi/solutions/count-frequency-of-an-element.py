import sys

def main():
    data = sys.stdin.read().split()
    if not data:
        return
    n = int(data[0])
    target = int(data[n + 1])
    freq = 0
    for i in range(1, n + 1):
        if int(data[i]) == target:
            freq += 1
    print(freq)

if __name__ == "__main__":
    main()
