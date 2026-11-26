import sys

def main():
    data = sys.stdin.read().strip().split()
    if not data:
        return
    it = iter(data)
    n = int(next(it))
    arr = [int(next(it)) for _ in range(n)]
    k = int(next(it))
    
    # deque of indices of negative numbers in current window, in order of appearance
    from collections import deque
    dq = deque()
    res = []
    
    for i, val in enumerate(arr):
        # remove indices that are out of the current window
        while dq and dq[0] <= i - k:
            dq.popleft()
        # if current value is negative, add its index to the deque
        if val < 0:
            dq.append(i)
        # if we have a full window (i >= k-1), output the first negative (if any)
        if i >= k - 1:
            res.append(str(arr[dq[0]]) if dq else "0")
    
    # print result space separated, no trailing space
    print(" ".join(res))

if __name__ == "__main__":
    main()
