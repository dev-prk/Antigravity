import sys
import heapq

def main():
    data = sys.stdin.read().strip().split()
    if not data:
        return
    n = int(data[0])
    k = int(data[1])
    arr = list(map(int, data[2:2+n]))
    result = heapq.nlargest(k, arr)[k-1]
    print(result)

if __name__ == "__main__":
    main()
