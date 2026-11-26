import sys

def main():
    data = sys.stdin.read().strip()
    if not data:
        return
    words = data.split()
    if len(words) >= 2:
        print(words[1], words[0])
    else:
        print(data)

if __name__ == "__main__":
    main()
