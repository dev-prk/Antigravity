import sys

def main():
    line = sys.stdin.readline().strip()
    
    if not line:
        print(-1)
        return
    
    # Handle negative numbers
    if line[0] == '-':
        line = line[1:]
    
    even_digits = []
    odd_digits = []
    
    for char in line:
        if char.isdigit():
            digit = int(char)
            if digit % 2 == 0:
                even_digits.append(digit)
            else:
                odd_digits.append(digit)
    
    # Sort and print
    if even_digits:
        print(' '.join(map(str, sorted(even_digits))))
    else:
        print(-1)
    
    if odd_digits:
        print(' '.join(map(str, sorted(odd_digits))))
    else:
        print(-1)

if __name__ == "__main__":
    main()
