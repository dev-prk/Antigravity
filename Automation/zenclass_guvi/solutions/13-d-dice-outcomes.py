import sys

MOD = 10**9 + 7

def main():
    data = sys.stdin.read().strip()
    if not data:
        return
    N = int(data)
    print(pow(13, N, MOD))

if __name__ == "__main__":
    main()
