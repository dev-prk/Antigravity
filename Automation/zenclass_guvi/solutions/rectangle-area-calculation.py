import sys

def main():
    # Read two natural numbers from stdin
    a = int(sys.stdin.readline().strip())
    b = int(sys.stdin.readline().strip())
    
    # Calculate area
    area = a * b
    
    # Round to first decimal place if required
    # If it's a whole number, print as integer
    # Otherwise, print with one decimal place
    rounded_area = round(area, 1)
    
    # Check if it's a whole number
    if rounded_area == int(rounded_area):
        print(int(rounded_area))
    else:
        print(rounded_area)

if __name__ == "__main__":
    main()
