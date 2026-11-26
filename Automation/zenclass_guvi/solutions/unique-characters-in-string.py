import sys

def main():
    s = sys.stdin.readline().rstrip('\n')
    seen = set()
    res = []
    for ch in s:
        if ch not in seen:
            seen.add(ch)
            res.append(ch)
    print(''.join(res))

if __name__ == "__main__":
    main()
