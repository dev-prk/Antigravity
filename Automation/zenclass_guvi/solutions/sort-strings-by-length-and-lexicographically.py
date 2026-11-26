import sys

def main():
    data = sys.stdin.read().strip().split()
    if not data:
        return
    n = int(data[0])
    strings = data[1:n+1]
    strings.sort(key=lambda x: (len(x), x))
    print(' '.join(strings))

if __name__ == "__main__":
    main()
