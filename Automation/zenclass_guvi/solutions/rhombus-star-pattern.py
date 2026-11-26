import sys

def main():
    line = sys.stdin.readline()
    if not line:
        return
    R = int(line.strip())
    for i in range(R):
        if i < R - 1:
            print(" " * (R - i - 1) + "*" * R)
        else:
            print("*" * R)

if __name__ == "__main__":
    main()
