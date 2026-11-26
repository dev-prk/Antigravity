import sys

def main():
    data = sys.stdin.read().strip().split()
    if not data:
        print(0)
        return
    n = int(data[0])
    # If n is 0, there are no numbers; output 0.
    if n == 0:
        print(0)
        return
    # Convert the next n tokens to integers.
    nums = list(map(int, data[1:1+n]))
    res = 0
    for x in nums:
        res |= x
    print(res)

if __name__ == "__main__":
    main()
