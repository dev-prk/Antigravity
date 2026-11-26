import sys

def main():
    n = int(sys.stdin.readline().strip())
    if n > 0:
        print("Positive")
    elif n < 0:
        print("Negative")
    else:
        print("Zero")

if __name__ == "__main__":
    main()
