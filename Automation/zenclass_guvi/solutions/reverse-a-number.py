import sys

def reverse_number(n):
    reversed_num = 0
    n = abs(n)
    while n > 0:
        reversed_num = reversed_num * 10 + n % 10
        n //= 10
    return reversed_num

def main():
    line = sys.stdin.readline()
    n = int(line.strip())
    print(reverse_number(n))

if __name__ == "__main__":
    main()
