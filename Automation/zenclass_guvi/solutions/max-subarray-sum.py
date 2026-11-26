import sys

def main():
    data = sys.stdin.read().strip().split()
    if not data:
        return
    n = int(data[0])
    if n == 0:
        print(0)
        return
    arr = list(map(int, data[1:1+n]))
    max_ending = max_sofar = arr[0]
    for x in arr[1:]:
        max_ending = max(x, max_ending + x)
        max_sofar = max(max_sofar, max_ending)
    print(max_sofar)

if __name__ == "__main__":
    main()
