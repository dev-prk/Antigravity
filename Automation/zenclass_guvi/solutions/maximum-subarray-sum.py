import sys

def main():
    data = sys.stdin.read().strip().split()
    if not data:
        return
    n = int(data[0])
    if n == 0:
        print(0)
        return
    arr = list(map(int, data[1:n+1]))
    if not arr:
        print(0)
        return
    max_sum = arr[0]
    current_sum = arr[0]
    for i in range(1, len(arr)):
        current_sum = max(arr[i], current_sum + arr[i])
        max_sum = max(max_sum, current_sum)
    print(max_sum)

if __name__ == "__main__":
    main()
