import sys

def main():
    data = sys.stdin.read().strip().split()
    if not data:
        return
    s = data[0]
    k = int(data[1])
    n = len(s)
    if n == 0:
        print("")
        return
    k_mod = k % n
    if k_mod == 0:
        print(s)
    else:
        print(s[-k_mod:] + s[:-k_mod])

if __name__ == "__main__":
    main()
