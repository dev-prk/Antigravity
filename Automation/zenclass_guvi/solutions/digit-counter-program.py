import sys

def main():
    line = sys.stdin.readline().strip()
    if not line:
        print(0)
        return
    num = int(line)
    if num == 0:
        print(1)
        return
    count = 0
    num = abs(num)
    while num > 0:
        count += 1
        num //= 10
    print(count)

if __name__ == "__main__":
    main()
