import sys

def main():
    data = sys.stdin.read().splitlines()
    n = int(data[0])
    nums = list(map(int, data[1].split()))
    out = []
    for x in nums:
        out.append("even" if x % 2 == 0 else "odd")
    print(" ".join(out))

if __name__ == "__main__":
    main()
