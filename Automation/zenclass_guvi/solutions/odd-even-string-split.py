import sys

def main():
    s = sys.stdin.readline().rstrip('\n')
    odd = s[0::2]
    even = s[1::2]
    print(f"{odd} {even}")

if __name__ == "__main__":
    main()
