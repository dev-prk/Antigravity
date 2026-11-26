import sys

def main():
    line = sys.stdin.readline()
    if not line:
        return
    R = int(line.strip())
    for _ in range(R):
        print('1' * R)

if __name__ == "__main__":
    main()
