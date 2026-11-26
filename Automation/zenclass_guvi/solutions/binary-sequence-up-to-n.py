import sys

def main():
    data = sys.stdin.read().split()
    if not data:
        return
    n = int(data[0])
    if n <= 0:
        print()
        return
    out = [bin(i)[2:] for i in range(1, n + 1)]
    sys.stdout.write(' '.join(out) + '\n')

if __name__ == '__main__':
    main()
