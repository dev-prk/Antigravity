import sys

def is_great_number(n):
    if n == 0:
        return True
    
    original_n = n
    m = 0  # sum of digits
    j = 1  # product of digits
    
    while n > 0:
        digit = n % 10
        m += digit
        j *= digit
        n //= 10
    
    return m + j == original_n

def main():
    line = sys.stdin.readline()
    n = int(line.strip())
    
    if is_great_number(n):
        print("Great")
    else:
        print("no")

if __name__ == "__main__":
    main()
