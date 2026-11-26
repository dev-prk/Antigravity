import sys
import threading


def print_numbers(N):
    s = 0
    for i in range(1, N + 1):
        print(i)
        s += i
    print(f"Sum: {s}")


def main():
    data = sys.stdin.read().split()
    if not data:
        return
    try:
        N = int(data[0])
    except ValueError:
        return

    t = threading.Thread(target=print_numbers, args=(N,))
    t.start()
    t.join()


if __name__ == "__main__":
    main()
