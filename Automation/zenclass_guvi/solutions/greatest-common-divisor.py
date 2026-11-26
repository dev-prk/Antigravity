import sys
import math

def main():
    data = sys.stdin.read().strip().split()
    if not data:
        return
    n = int(data[0])
    if n == 0:
        print(-1)
        return
    arr = list(map(int, data[1:n+1]))
    if len(arr) == 0:
        print(-1)
        return
    arr = [abs(x) for x in arr]
    result = arr[0]
    for i in range(1, len(arr)):
        result = math.gcd(result, arr[i])
    print(result)

if __name__ == "__main__":
    main()
