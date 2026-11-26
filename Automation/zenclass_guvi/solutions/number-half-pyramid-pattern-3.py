import sys

def main():
    data = sys.stdin.read().strip()
    if not data:
        return
    R = int(data)
    for i in range(R):
        start = R - i
        line = ''.join(str(j) for j in range(start, 0, -1))
        print(line)

if __name__ == "__main__":
    main()
