import sys

def josephus(n, k):
    if n == 0:
        return 0
    result = 0
    for i in range(1, n + 1):
        result = (result + k) % i
    return result + 1

def main():
    data = sys.stdin.read().strip().split()
    if len(data) < 2:
        return
    n = int(data[0])
    k = int(data[1])
    print(josephus(n, k))

if __name__ == "__main__":
    main()
