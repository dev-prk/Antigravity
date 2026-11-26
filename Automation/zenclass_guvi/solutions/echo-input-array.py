import sys

def main():
    lines = sys.stdin.read().splitlines()
    for line in lines:
        if line.strip():
            print(line)

if __name__ == "__main__":
    main()
