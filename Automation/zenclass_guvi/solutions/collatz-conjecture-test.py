import sys

def main():
    data = sys.stdin.read().strip().split()
    if not data:
        return
    n = int(data[0])
    seq = []
    if n <= 0:
        seq.append(str(n))
    else:
        while True:
            seq.append(str(n))
            if n == 1:
                break
            if n % 2 == 0:
                n //= 2
            else:
                n = 3 * n + 1
    sys.stdout.write(' '.join(seq))

if __name__ == "__main__":
    main()
