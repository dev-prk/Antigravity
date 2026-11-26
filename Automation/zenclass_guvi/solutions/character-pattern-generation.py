import sys

def main():
    data = sys.stdin.read().split()
    if not data:
        return
    n = int(data[0])
    out = []
    for i in range(n):
        out.append('b' * i + '*' * (n - i))
    sys.stdout.write('\n'.join(out))

if __name__ == "__main__":
    main()
