import sys

def main():
    s = sys.stdin.readline().strip()
    vowels = set('aeiouAEIOU')
    filtered = ''.join(ch for ch in s if ch not in vowels)
    if not filtered:
        print('-1')
    else:
        print(filtered[::-1])

if __name__ == '__main__':
    main()
