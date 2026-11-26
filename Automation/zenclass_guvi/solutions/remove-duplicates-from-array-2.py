import sys

def main():
    data = sys.stdin.buffer.read().split()
    if not data:
        return
    n = int(data[0])
    values = list(map(int, data[1:1 + n]))
    counts = {}
    for v in values:
        counts[v] = counts.get(v, 0) + 1
    result = [str(v) for v in values if counts[v] == 1]
    output = ' '.join(result)
    if output:
        sys.stdout.write(output + '\n')

if __name__ == '__main__':
    main()
