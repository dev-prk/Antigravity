import sys

def main():
    data = sys.stdin.read().strip().split()
    if not data:
        return
    try:
        n = int(data[0])
    except:
        # if first token is not integer, treat all as strings
        strings = data
        strings.sort()
        sys.stdout.write(' '.join(strings))
        return

    strings = data[1:1 + max(0, n)]
    strings.sort()
    sys.stdout.write(' '.join(strings))

if __name__ == "__main__":
    main()
