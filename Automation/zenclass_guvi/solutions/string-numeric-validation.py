import sys

def main():
    s = sys.stdin.readline().strip()
    if s.isdigit():
        print("yes")
    else:
        print("no")

if __name__ == "__main__":
    main()
