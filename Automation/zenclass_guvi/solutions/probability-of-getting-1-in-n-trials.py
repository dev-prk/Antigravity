def main():
    import sys
    n = int(sys.stdin.readline().strip())
    
    if n == 0:
        print("0 1")
        return
    
    # Calculate 6^n and 5^n
    six_power = 6 ** n
    five_power = 5 ** n
    
    numerator = six_power - five_power
    denominator = six_power
    
    # Reduce the fraction to simplest form
    def gcd(a, b):
        while b:
            a, b = b, a % b
        return a
    
    g = gcd(numerator, denominator)
    numerator //= g
    denominator //= g
    
    print(f"{numerator} {denominator}")

if __name__ == "__main__":
    main()
