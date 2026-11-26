import sys

def main():
    n = int(sys.stdin.readline().strip())
    if n <= 0:
        print(-1)
        return
    result = []
    value = 1
    for i in range(n):
        result.append(str(value))
        value *= 2
    print(' '.join(result))

if __name__ == "__main__":
    main()
