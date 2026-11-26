import sys

def solve():
    data = sys.stdin.read().strip().split()
    if not data:
        return
    try:
        R = int(data[0])
    except:
        return
    for i in range(R, 0, -1):
        line = ''.join(str(j) for j in range(1, 2 * i))
        print(line)

if __name__ == "__main__":
    solve()
