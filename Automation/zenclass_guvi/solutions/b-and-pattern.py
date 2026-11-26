import sys

def main():
    data = sys.stdin.read().strip()
    if not data:
        return
    R = int(data)
    width = 2 * R - 1
    for i in range(R):
        line = 'b' * i + '*' * (width - 2 * i) + 'b' * i
        print(line)

if __name__ == "__main__":
    main()
