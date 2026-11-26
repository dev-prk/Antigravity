import sys

def main():
    data = sys.stdin.read().split()
    if not data:
        return
    try:
        R = int(data[0])
    except (ValueError, IndexError):
        return
    
    if R < 1 or R > 100:
        return
    
    for i in range(R):
        leading_spaces = i
        num_letters = R - i
        line = ' ' * leading_spaces
        line += ''.join(chr(ord('A') + j) for j in range(num_letters))
        print(line)

if __name__ == "__main__":
    main()
