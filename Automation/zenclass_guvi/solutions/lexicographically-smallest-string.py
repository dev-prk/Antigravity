import sys

def main():
    data = sys.stdin.read().split()
    if not data:
        return
    n = int(data[0])
    strings = data[1:1 + n]
    if strings:
        print(min(strings))

if __name__ == "__main__":
    main()
