def main():
    import sys
    n = sys.stdin.readline().strip()
    
    if not n:
        print(0)
        return
    
    # Handle negative numbers
    if n[0] == '-':
        n = n[1:]
    
    # Check if there are at least 2 digits
    if len(n) < 2:
        print(0)
        return
    
    # Get first two digits
    d1 = int(n[0])
    d2 = int(n[1])
    
    # Calculate sum
    s = d1 + d2
    
    # Convert sum to string
    s_str = str(s)
    
    # Check if s_str appears in n
    if s_str in n:
        print(1)
    else:
        print(0)

if __name__ == "__main__":
    main()
