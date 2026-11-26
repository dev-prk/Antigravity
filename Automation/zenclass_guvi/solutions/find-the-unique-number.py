import sys

def main():
    data = sys.stdin.read().strip().split()
    if not data:
        return
    n = int(data[0])
    if n == 0:
        print(-1)
        return
    nums = list(map(int, data[1:n+1]))
    result = 0
    for num in nums:
        result ^= num
    print(result)

if __name__ == "__main__":
    main()
