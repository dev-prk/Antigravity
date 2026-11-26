import sys

def main():
    line = sys.stdin.readline()
    if not line:
        return
    n = int(line.strip())
    if n % 2 == 0:
        print("Even")
    else:
        print("oDd")

if __name__ == "__main__":
    main()
