import sys

def main():
    data = sys.stdin.read().split()
    if not data:
        return
    n = int(data[0])
    if n == 0:
        print()
        return
    values = list(map(int, data[1:1 + n]))
    count0 = values.count(0)
    count1 = values.count(1)
    count2 = values.count(2)
    result = [0] * count0 + [1] * count1 + [2] * count2
    sys.stdout.write(' '.join(map(str, result)) + '\n')

if __name__ == '__main__':
    main()
