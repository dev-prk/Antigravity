import sys

def main():
    line = sys.stdin.readline().strip()
    if not line:
        return
    parts = line.rsplit(' ', 1)
    if len(parts) < 2:
        print(line)
        return
    s = parts[0].rstrip()
    try:
        k = int(parts[1])
    except ValueError:
        print(s)
        return
    if k <= 0 or k > len(s):
        print(s)
        return
    res = []
    for i in range(len(s)):
        if (i + 1) % k == 0:
            res.append(s[i].upper())
        else:
            res.append(s[i])
    print(''.join(res))

if __name__ == "__main__":
    main()
