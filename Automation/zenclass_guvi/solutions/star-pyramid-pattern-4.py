import sys

def main():
    line = sys.stdin.readline()
    if not line:
        return
    R = int(line.rstrip())
    
    for i in range(R):
        spaces = ' ' * i
        stars = '*' * (R - i)
        sys.stdout.write(spaces + stars + '\n')

if __name__ == "__main__":
    main()
