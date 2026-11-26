import sys


def main():
    data = sys.stdin.read().split()
    if not data:
        return
    n = int(data[0])
    sys.stdout.write(str(~n) + "\n")


main()
