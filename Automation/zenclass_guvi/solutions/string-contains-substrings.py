import sys

def main():
    s = sys.stdin.readline().rstrip('\n')
    has_guvi = 'GUVI' in s
    has_geek = 'GEEK' in s
    print('yes' if has_guvi and has_geek else 'no')

if __name__ == "__main__":
    main()
