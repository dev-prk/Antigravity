import sys
import bisect

def main():
    data = sys.stdin.read().strip().split()
    if not data:
        print(0)
        return
    n = int(data[0])
    if n == 0:
        print(0)
        return
    arr = list(map(int, data[1:n+1]))
    tails = []
    for num in arr:
        idx = bisect.bisect_left(tails, num)
        if idx == len(tails):
            tails.append(num)
        else:
            tails[idx] = num
    print(len(tails))

if __name__ == "__main__":
    main()
