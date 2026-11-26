import sys

def main():
    data = sys.stdin.read().split()
    if not data:
        return
    n = int(data[0])
    numbers = list(map(int, data[1:1 + n])) if n > 0 else []
    total = sum(numbers)
    print('even' if total % 2 == 0 else 'odd')

if __name__ == '__main__':
    main()
