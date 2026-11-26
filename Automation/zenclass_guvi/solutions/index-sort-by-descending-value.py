import sys

def main():
    data = sys.stdin.read().split()
    if not data:
        return
    f = int(data[0])
    arr = list(map(int, data[1:1+f]))
    indices = list(range(f))
    indices.sort(key=lambda i: (-arr[i], i))
    print(' '.join(map(str, indices)))

if __name__ == "__main__":
    main()
