import sys

def main():
    line = sys.stdin.readline().strip()
    if not line:
        return
    R = int(line)
    for i in range(R, 0, -1):
        print(''.join(str(j) for j in range(1, i + 1)))

if __name__ == "__main__":
    main()
