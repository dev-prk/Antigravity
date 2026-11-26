import sys

def main():
    line = sys.stdin.readline().strip()
    if not line:
        print(0)
        return
    num = int(line)
    count = 0
    n = abs(num)
    if n == 0:
        print(1)
        return
    while n > 0:
        n //= 10
        count += 1
    print(count)

if __name__ == "__main__":
    main()
