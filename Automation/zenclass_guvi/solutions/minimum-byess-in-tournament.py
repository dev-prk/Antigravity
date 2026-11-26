import sys

def main():
    N = int(sys.stdin.readline())
    low = 1 << (N.bit_length() - 1)
    lower_diff = N - low
    high = low << 1
    upper_diff = high - N
    print(min(lower_diff, upper_diff))

if __name__ == "__main__":
    main()
