import sys

def main():
    n = int(sys.stdin.readline().strip())
    start_char = ord('a')
    for i in range(n):
        # Each line starts with i spaces, then characters from (start_char + i) to (start_char + n)
        line = ' ' * i + ''.join(chr(start_char + j) for j in range(i, n))
        print(line)

if __name__ == "__main__":
    main()
