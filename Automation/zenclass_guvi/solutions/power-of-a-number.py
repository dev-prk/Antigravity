import sys

def is_power(n, k):
    # Special cases
    if n == 1:
        return True  # k^0 = 1 for any k != 0
    if k == 1:
        return n == 1
    if k == -1:
        return n == 1 or n == -1
    if n == 0:
        return False
    if k == 0:
        return False  # 0^0 undefined, 0^positive = 0 but we need n == 0 which we excluded
    
    # Handle negative numbers
    if n < 0 and k > 0:
        return False
    if n > 0 and k < 0:
        # positive = negative^even, need to check if abs(n) is power of abs(k)
        # with even exponent
        temp = abs(n)
        abs_k = abs(k)
        while temp > 1:
            if temp % abs_k != 0:
                return False
            temp //= abs_k
        return True
    
    if n < 0 and k < 0:
        # negative = negative^odd, check with abs values and odd exponent
        temp = abs(n)
        abs_k = abs(k)
        count = 0
        while temp > 1:
            if temp % abs_k != 0:
                return False
            temp //= abs_k
            count += 1
        return count % 2 == 1
    
    # n > 0 and k > 0
    temp = n
    while temp > 1:
        if temp % k != 0:
            return False
        temp //= k
    return True

def main():
    data = sys.stdin.read().strip().split()
    if len(data) < 2:
        return
    n = int(data[0])
    k = int(data[1])
    
    if is_power(n, k):
        print("yes")
    else:
        print("no")

if __name__ == "__main__":
    main()
