import sys

def main():
    line = sys.stdin.readline()
    if line.endswith('\n'):
        line = line[:-1]
    if not line:
        return
    out = []
    cur = line[0]
    cnt = 1
    for ch in line[1:]:
        if ch == cur:
            cnt += 1
        else:
            out.append(cur)
            out.append(str(cnt))
            cur = ch
            cnt = 1
    out.append(cur)
    out.append(str(cnt))
    sys.stdout.write(''.join(out))

if __name__ == "__main__":
    main()
