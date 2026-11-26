import sys

def next_permutation(s: str):
    a = list(s)
    n = len(a)
    i = n - 2
    while i >= 0 and a[i] >= a[i + 1]:
        i -= 1
    if i < 0:
        return None
    j = n - 1
    while a[j] <= a[i]:
        j -= 1
    a[i], a[j] = a[j], a[i]
    a[i + 1:] = reversed(a[i + 1:])
    return ''.join(a)

def main():
    out = []
    for line in sys.stdin:
        s = line.strip()
        if not s:
            continue
        res = next_permutation(s)
        out.append(res if res is not None else "-1")
    sys.stdout.write("\n".join(out))

if __name__ == "__main__":
    main()
