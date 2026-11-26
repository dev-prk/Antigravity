import sys

def solve():
    data = sys.stdin.read()
    if not data:
        return
    # Remove trailing newline characters but keep other whitespace
    data = data.rstrip('\n')
    # Remove carriage returns if any
    data = data.replace('\r', '')
    sys.stdout.write(data.replace('a', '$'))

if __name__ == "__main__":
    solve()
