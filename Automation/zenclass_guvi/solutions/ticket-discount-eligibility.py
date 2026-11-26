import sys

def main():
    data = sys.stdin.read().split()
    if not data:
        return
    idx = 0
    n = int(data[idx])
    idx += 1
    tickets = []
    for i in range(n):
        tickets.append(int(data[idx]))
        idx += 1
    k = int(data[idx])
    res = []
    for t in tickets:
        if k != 0 and t % k == 0:
            res.append('1')
        else:
            res.append('0')
    sys.stdout.write(' '.join(res))

if __name__ == '__main__':
    main()
