import sys

def main():
    R = int(sys.stdin.readline().strip())
    
    # Print the first star line
    print('*')
    
    # Upper half (including middle row)
    for i in range(1, R + 1):
        # Build the number part: 123...i...321
        left_part = ''.join(str(j) for j in range(1, i + 1))
        right_part = ''.join(str(j) for j in range(i - 1, 0, -1))
        print('*' + left_part + right_part + '*')
    
    # Lower half (excluding middle row)
    for i in range(R - 1, 0, -1):
        # Build the number part: 123...i...321
        left_part = ''.join(str(j) for j in range(1, i + 1))
        right_part = ''.join(str(j) for j in range(i - 1, 0, -1))
        print('*' + left_part + right_part + '*')
    
    # Print the final single star
    print('*')

if __name__ == "__main__":
    main()
