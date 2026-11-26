import sys

def main():
    data = sys.stdin.read().split()
    if len(data) < 2:
        print('no')
        return
    s1, s2 = data[0], data[1]
    print('yes' if s1 == s2 else 'no')

if __name__ == "__main__":
    main()
