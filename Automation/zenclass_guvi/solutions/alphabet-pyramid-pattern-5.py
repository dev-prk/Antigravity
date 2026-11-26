import sys

def main():
    data = sys.stdin.read().strip()
    if not data:
        return
    R = int(data)
    
    for i in range(1, R + 1):
        # Calculate leading spaces: (R - i) spaces
        leading_spaces = ' ' * (R - i)
        
        # Calculate number of letters in this row: 2*i - 1
        num_letters = 2 * i - 1
        
        # Get the letter for this row (0-indexed: 0='A', 1='B', etc.)
        letter = chr(ord('A') + (i - 1))
        
        # Create the row: leading spaces + letters
        row = leading_spaces + letter * num_letters
        
        print(row)

if __name__ == "__main__":
    main()
