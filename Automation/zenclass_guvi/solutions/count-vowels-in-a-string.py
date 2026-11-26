import sys

def main():
    s = sys.stdin.readline().strip()
    vowels = set('aeiouAEIOU')
    count = sum(1 for char in s if char in vowels)
    print(count)

if __name__ == "__main__":
    main()
