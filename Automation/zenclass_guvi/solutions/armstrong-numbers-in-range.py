import sys

def is_armstrong(n):
    if n < 0:
        return False
    digits = [int(d) for d in str(n)]
    power = len(digits)
    return sum(d ** power for d in digits) == n

def main():
    data = sys.stdin.read().strip().split()
    if not data:
        print("No elements")
        return
    start, end = int(data[0]), int(data[1])
    armstrong_nums = [str(n) for n in range(start, end + 1) if is_armstrong(n)]
    if not armstrong_nums:
        print("No elements")
    else:
        print(" ".join(armstrong_nums))

if __name__ == "__main__":
    main()
