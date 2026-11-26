import sys

def solve():
    data = sys.stdin.read().strip().split()
    if not data:
        return
    n = int(data[0])
    arr = list(map(int, data[1:1+n]))
    if n <= 1:
        print("yes")
        return
    prev_sign = None
    for i in range(n-1):
        diff = arr[i+1] - arr[i]
        if diff > 0:
            cur = 'pos'
        elif diff < 0:
            cur = 'neg'
        else:
            print("no")
            return
        if prev_sign is None:
            prev_sign = cur
        else:
            if cur == prev_sign:
                print("no")
                return
            prev_sign = cur
    print("yes")

if __name__ == "__main__":
    solve()
