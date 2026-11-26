import sys

def main():
    data = sys.stdin.read().strip()
    if not data:
        return
    R = int(data)
    
    for i in range(R):
        # Calculate the character: A maps to position R, B to R-1, etc.
        char_pos = R - i
        # Convert to uppercase letter: 0->A, 1->B, etc.
        ch = chr(ord('A') + char_pos - 1)
        # Number of characters on this row: R - i
        count = R - i
        # Leading spaces: i spaces
        spaces = ' ' * i
        # The characters
        chars = ch * count
        # Print the row
        print(spaces + chars)

if __name__ == "__main__":
    main()
