import sys

def main():
    data = sys.stdin.read().strip()
    if not data:
        return
    R = int(data)
    
    for i in range(R):
        leading_spaces = ' ' * (R - 1 - i)
        letters = ''.join(chr(ord('A') + j) for j in range(2 * i + 1))
        print(leading_spaces + letters)

if __name__ == "__main__":
    main()
