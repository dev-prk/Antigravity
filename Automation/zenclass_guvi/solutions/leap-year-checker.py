import sys

def main():
    year = int(sys.stdin.readline().strip())
    is_leap = (year % 4 == 0 and year % 100 != 0) or (year % 400 == 0)
    print(is_leap)

if __name__ == "__main__":
    main()
