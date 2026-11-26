import sys

def count_set_bits(n):
    count = 0
    while n:
        count += n & 1
        n >>= 1
    return count

def main():
    line = sys.stdin.readline()
    if not line:
        return
    n = int(line.strip())
    print(count_set_bits(n))

if __name__ == "__main__":
    main()
