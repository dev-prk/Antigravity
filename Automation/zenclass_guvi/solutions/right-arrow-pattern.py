import sys

def main():
    R = int(sys.stdin.readline().strip())
    
    # Upper part: R-1 rows with right-aligned single star
    for i in range(1, R):
        spaces = ' ' * (R - i)
        print(spaces + '*')
    
    # Middle row: R stars
    print('*' * R)
    
    # Lower part: R-1 rows with right-aligned single star
    for i in range(1, R):
        spaces = ' ' * i
        print(spaces + '*')

if __name__ == "__main__":
    main()
