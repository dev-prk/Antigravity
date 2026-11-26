import sys

def main():
    data = sys.stdin.read().split()
    if not data:
        return
    year = int(data[0])
    if (year % 4 == 0 and year % 100 != 0) or (year % 400 == 0):
        print("leap year")
    else:
        print("not a leap year")

if __name__ == "__main__":
    main()
