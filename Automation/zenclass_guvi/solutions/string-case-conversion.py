import sys

def main():
    s = sys.stdin.readline()
    if s.endswith('\n'):
        s = s[:-1]  # remove only the trailing newline
    sys.stdout.write(s.swapcase())

if __name__ == "__main__":
    main()
