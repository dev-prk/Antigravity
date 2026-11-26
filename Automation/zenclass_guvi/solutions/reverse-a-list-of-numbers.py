import sys

def main():
    data = sys.stdin.read().strip().split()
    if not data:
        return
    n = int(data[0])
    numbers = list(map(int, data[1:1+n]))
    reversed_numbers = numbers[::-1]
    print('->'.join(map(str, reversed_numbers)))

if __name__ == "__main__":
    main()
