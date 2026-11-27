import sys

def main():
    data = sys.stdin.read().strip().split()
    if not data:
        print(-1)
        return
    
    n = int(data[0])
    if len(data) < 2:
        print(-1)
        return
    
    ages = list(map(int, data[1:1+n]))
    
    if not ages:
        print(-1)
        return
    
    # Desired sum (actual ages)
    desired_sum = sum(ages)
    
    # Binary equivalent sum (treating binary representation as decimal integer)
    binary_sum = 0
    for age in ages:
        # Get binary representation and interpret it as a decimal number
        binary_str = bin(age)[2:]  # Remove '0b' prefix
        binary_sum += int(binary_str)
    
    # Magnitude of deviation
    deviation = abs(desired_sum - binary_sum)
    print(deviation)

if __name__ == "__main__":
    main()
