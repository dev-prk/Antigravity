import sys

def main():
    data = sys.stdin.read().strip()
    if not data:
        return
    n = int(data)
    if n <= 0:
        return
    dfg = [1]
    i2 = i3 = i5 = 0
    while len(dfg) < n:
        next2 = dfg[i2] * 2
        next3 = dfg[i3] * 3
        next5 = dfg[i5] * 5
        nxt = min(next2, next3, next5)
        dfg.append(nxt)
        if nxt == next2:
            i2 += 1
        if nxt == next3:
            i3 += 1
        if nxt == next5:
            i5 += 1
    print(' '.join(map(str, dfg)))

if __name__ == "__main__":
    main()
