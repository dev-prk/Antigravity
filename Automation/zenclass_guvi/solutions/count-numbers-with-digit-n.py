import sys

def count_numbers_with_digit(l, r, n):
    count = 0
    for num in range(l, r + 1):
        if str(n) in str(num):
            count += 1
    return count

def main():
    line = sys.stdin.readline().strip()
    if not line:
        return
    parts = line.split()
    l = int(parts[0])
    r = int(parts[1])
    n = int(parts[2])
    result = count_numbers_with_digit(l, r, n)
    print(result)

if __name__ == "__main__":
    main()
