import sys

def main():
    data = sys.stdin.read().strip()
    if not data:
        return
    R = int(data)
    
    for i in range(R):
        if i == 0 or i == R - 1:
            # First and last line: solid star line
            print(' ' * (R - 1 - i) + '*' * R)
        else:
            # Middle lines: hollow rhombus pattern
            print(' ' * (R - 1 - i) + '*' + ' ' * (R - 2) + '*')

if __name__ == "__main__":
    main()
