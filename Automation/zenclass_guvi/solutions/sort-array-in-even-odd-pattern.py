import sys

def main():
    data = sys.stdin.read().split()
    if not data:
        return
    n = int(data[0])
    if n == 0:
        print()
        return
    arr = list(map(int, data[1:1+n]))
    evens = [x for x in arr if x % 2 == 0]
    odds = [x for x in arr if x % 2 != 0]
    evens.sort()
    odds.sort(reverse=True)
    result = evens + odds
    print(' '.join(map(str, result)))

if __name__ == "__main__":
    main()
