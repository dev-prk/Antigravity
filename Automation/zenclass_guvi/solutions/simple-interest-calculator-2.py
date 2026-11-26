import sys

def main():
    # Read all lines and strip whitespace
    lines = [line.strip() for line in sys.stdin.readlines()]
    
    # Filter out empty lines
    values = [line for line in lines if line]
    
    # Parse the three inputs
    principal = float(values[0])
    time = int(values[1])
    rate = float(values[2])
    
    # Calculate simple interest: (P * T * R) / 100
    simple_interest = (principal * time * rate) / 100
    
    # Print the result
    print(simple_interest)

if __name__ == "__main__":
    main()
