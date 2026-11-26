import sys

def main():
    year = int(sys.stdin.readline().strip())
    if (year % 4 == 0 and year % 100 != 0) or (year % 400 == 0):
        print("Y")
    else:
        print("N")

if __name__ == "__main__":
    main()
