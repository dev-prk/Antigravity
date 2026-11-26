import sys

def main():
    data = sys.stdin.read().strip()
    if not data:
        return
    # Remove leading sign if present
    if data[0] == '-':
        data = data[1:]
    # Sum all digit characters
    total = sum(int(ch) for ch in data if ch.isdigit())
    print(total)

if __name__ == "__main__":
    main()
