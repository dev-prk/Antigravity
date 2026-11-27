import sys

def main():
    data = sys.stdin.read().strip()
    if not data:
        print(-1)
        return
    try:
        R = int(data)
    except ValueError:
        print(-1)
        return
    if R < 1 or R > 100:
        print(-1)
        return
    for i in range(R):
        leading_spaces = ' ' * (R - i - 1)
        stars = '* ' * (i + 1)
        stars = stars.rstrip()
        print(leading_spaces + stars)

if __name__ == "__main__":
    main()
