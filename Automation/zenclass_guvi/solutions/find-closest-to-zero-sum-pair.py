import sys

def main():
    data = sys.stdin.read().strip().split()
    if not data:
        return
    n = int(data[0])
    if n == 0:
        return
    arr = list(map(int, data[1:n+1]))
    if n == 1:
        return
    arr.sort()
    left = 0
    right = n - 1
    best_sum = float('inf')
    best_pair = (arr[left], arr[right])
    while left < right:
        curr_sum = arr[left] + arr[right]
        if abs(curr_sum) < abs(best_sum):
            best_sum = curr_sum
            best_pair = (arr[left], arr[right])
        if curr_sum < 0:
            left += 1
        elif curr_sum > 0:
            right -= 1
        else:
            break
    print(best_pair[1], best_pair[0])

if __name__ == "__main__":
    main()
