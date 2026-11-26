import sys
import math

def main():
    line = sys.stdin.readline().strip()
    if not line:
        print(-1)
        return
    if line.startswith('p=[') and line.endswith(']'):
        line = line[3:-1]
    if not line:
        print(-1)
        return
    parts = line.split(',')
    try:
        p = [int(x.strip()) for x in parts if x.strip()]
    except:
        print(-1)
        return
    if not p:
        print(-1)
        return
    n = len(p)
    for x in p:
        if x < 1 or x > n:
            print(-1)
            return
    visited = [False] * n
    cycle_lengths = []
    for i in range(n):
        if not visited[i]:
            length = 0
            current = i
            while not visited[current]:
                visited[current] = True
                current = p[current] - 1
                length += 1
            if length > 0:
                cycle_lengths.append(length)
    if not cycle_lengths:
        print(-1)
        return
    result = 1
    for cl in cycle_lengths:
        result = result * cl // math.gcd(result, cl)
    print(result)

if __name__ == "__main__":
    main()
