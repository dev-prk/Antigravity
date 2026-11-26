import sys

def main():
    data = sys.stdin.read().split()
    if not data:
        return
    try:
        R = int(data[0])
    except ValueError:
        return
    for i in range(1, R + 1):
        print(''.join(str(j) for j in range(1, i + 1)))

if __name__ == '__main__':
    main()
