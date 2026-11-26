import sys

def main():
    line = sys.stdin.readline().strip()
    result = []
    for char in line:
        if char.isdigit():
            result.append(char)
    print(''.join(result))

if __name__ == "__main__":
    main()
