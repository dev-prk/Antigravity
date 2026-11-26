import sys

def main():
    s = sys.stdin.read()
    if not s:
        print(0)
        return
    # Remove trailing newlines that are not part of the intended string
    s = s.rstrip('\n\r')
    count = sum(1 for ch in s if ch != ' ' and ch != '\n' and ch != '\r')
    print(count)

if __name__ == "__main__":
    main()
