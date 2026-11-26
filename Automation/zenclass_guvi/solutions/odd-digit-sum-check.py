import sys

def main():
    line = sys.stdin.readline().strip()
    if not line:
        print('E')
        return
    
    n = int(line)
    total = 0
    
    while n > 0:
        digit = n % 10
        if digit % 2 == 1:
            total += digit
        n //= 10
    
    if total % 2 == 0:
        print('E')
    else:
        print('O')

if __name__ == "__main__":
    main()
