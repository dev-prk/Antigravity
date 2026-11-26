import sys

def main():
    data = sys.stdin.read().strip().split()
    if not data:
        return
    n = int(data[0])
    if n == 0:
        return
    salaries = list(map(int, data[1:1+n]))
    salaries.sort()
    print(' '.join(map(str, salaries)))

if __name__ == "__main__":
    main()
