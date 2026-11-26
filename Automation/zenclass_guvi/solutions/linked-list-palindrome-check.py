import sys

def main():
    data = sys.stdin.read().split()
    if not data:
        print("yes")
        return
    n = int(data[0])
    if n <= 0:
        print("yes" if n == 0 else "no")
        return
    tokens = data[1:1+n]
    # In case there are fewer tokens than n, take what's available
    if len(tokens) < n:
        # pad or just use available? Typically input is well-formed.
        pass
    if tokens == tokens[::-1]:
        print("yes")
    else:
        print("no")

if __name__ == "__main__":
    main()
