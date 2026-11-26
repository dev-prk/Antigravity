import sys

def main():
    data = sys.stdin.read().split()
    if not data:
        print(0)
        return
    n = int(data[0])
    arr = list(map(int, data[1:1+n]))
    # In case of missing numbers, just use what is available
    count = 0
    for k in range(len(arr)):
        target = arr[k]
        freq = {}
        for j in range(k):
            need = target - arr[j]
            count += freq.get(need, 0)
            freq[arr[j]] = freq.get(arr[j], 0) + 1
    print(count)

if __name__ == "__main__":
    main()
