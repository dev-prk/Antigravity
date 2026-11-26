import sys

def main():
    data = sys.stdin.read().split()
    if not data:
        print('no')
        return
    s = data[0]
    p = data[1] if len(data) > 1 else ''
    print('yes' if p in s else 'no')

if __name__ == "__main__":
    main()
