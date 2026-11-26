import sys

def main():
    data = sys.stdin.buffer.read().split()
    if not data:
        return
    n = int(data[0])
    if n <= 0:
        return
    vals = data[1:1 + n]
    result = []
    total = 0
    for x in vals:
        total += int(x)
        result.append(str(total))
    sys.stdout.write(' '.join(result) + '\n')

if __name__ == "__main__":
    main()
