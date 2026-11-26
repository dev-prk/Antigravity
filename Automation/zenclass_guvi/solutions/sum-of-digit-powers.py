import sys

def main():
    data = sys.stdin.read().strip()
    if not data:
        return
    s = data.lstrip('-+').strip()
    if s == '':
        s = '0'
    num_digits = len(s)
    total = 0
    for ch in s:
        d = int(ch)
        total += d ** num_digits
    print(total)

if __name__ == "__main__":
    main()
