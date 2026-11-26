import sys

def main():
    data = sys.stdin.read().strip()
    if not data:
        return
    n = data.strip()
    digit_sum = sum(int(ch) for ch in n)
    s = str(digit_sum)
    if s == s[::-1]:
        print("yes")
    else:
        print("no")

if __name__ == "__main__":
    main()
