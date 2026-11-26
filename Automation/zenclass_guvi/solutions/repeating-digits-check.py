import sys

def main():
    line = sys.stdin.readline().strip()
    if not line:
        print('no')
        return
    digits = line.replace('-', '').replace(' ', '')
    if len(digits) != len(set(digits)):
        print('yes')
    else:
        print('no')

if __name__ == "__main__":
    main()
