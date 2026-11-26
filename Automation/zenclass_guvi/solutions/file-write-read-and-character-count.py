import sys

def main():
    s = sys.stdin.readline()
    if s.endswith('\n'):
        s = s[:-1]

    with open('output.txt', 'w', encoding='utf-8') as f:
        f.write(s)

    with open('output.txt', 'r', encoding='utf-8') as f:
        content = f.read()

    print(content)
    print(f"Character Count: {len(s)}")

if __name__ == "__main__":
    main()
