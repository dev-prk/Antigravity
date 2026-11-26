import sys

def main():
    nums = list(map(int, sys.stdin.read().split()))
    
    max_even = None
    max_odd = None
    
    for x in nums:
        if x % 2 == 0:
            if max_even is None or x > max_even:
                max_even = x
        else:
            if max_odd is None or x > max_odd:
                max_odd = x
                
    even_value = -1 if max_even is None else max_even
    odd_value = -1 if max_odd is None else max_odd
    
    print(f"Largest even:{even_value}")
    print(f"Largest odd:{odd_value}")

if __name__ == "__main__":
    main()
