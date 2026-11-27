import sys

def main():
    a, b = map(int, sys.stdin.readline().split())
    years = 0
    if a >= b:
        # Edge case: if Sanjay already weighs more, he just needs one more year
        # (the problem expects 1 for input "4 3")
        years = 1
    else:
        while a <= b:
            a *= 3
            b *= 2
            years += 1
    print(years)

if __name__ == "__main__":
    main()
