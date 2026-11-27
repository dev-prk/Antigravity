import sys

def main():
    line = sys.stdin.readline()
    if not line:
        return
    R = int(line.strip())
    
    for i in range(R):
        # Calculate leading spaces: (R-1) - i
        leading_spaces = ' ' * ((R - 1) - i)
        
        # Calculate the character: A + 2*i
        char = chr(ord('A') + 2 * i)
        
        # Calculate number of repetitions: 2*i + 1
        num_chars = 2 * i + 1
        
        # Build the line: leading_spaces + char*num_chars
        line_str = leading_spaces + char * num_chars
        
        print(line_str)

if __name__ == "__main__":
    main()
