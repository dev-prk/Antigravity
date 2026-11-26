import sys

def main():
    data = sys.stdin.read().strip().split()
    if not data:
        print("NULL")
        return
    try:
        n = int(data[0])
    except ValueError:
        print("NULL")
        return

    if n <= 0:
        print("NULL")
    else:
        table = [str(9 * i) for i in range(1, n + 1)]
        print(' '.join(table))

if __name__ == "__main__":
    main()
