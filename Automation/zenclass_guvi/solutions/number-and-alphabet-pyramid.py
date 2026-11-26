import sys

def main():
    data = sys.stdin.read().split()
    if not data:
        return
    R = int(data[0])
    
    for i in range(1, R + 1):
        # Leading spaces: R - i spaces
        spaces = ' ' * (R - i)
        
        # Letters: A, B, C, ... up to i letters
        letters = ''.join(chr(ord('A') + j) for j in range(i))
        
        # Numbers: 1, 2, 3, ... up to i numbers
        numbers = ''.join(str(j + 1) for j in range(i))
        
        # Combine all parts
        line = spaces + letters + numbers
        print(line)

if __name__ == "__main__":
    main()
