import sys

def main():
    n = int(sys.stdin.readline().strip())
    s = str(n)
    total = 0
    for i in range(len(s)):
        digit = int(s[i])
        total += digit ** i
    print(total)

if __name__ == "__main__":
    main()
