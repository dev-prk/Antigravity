import sys

def main():
    # Read all lines from stdin
    lines = [line.strip() for line in sys.stdin if line.strip()]
    
    # Parse each line into a list of integers
    main_rows = []
    for line in lines:
        row = list(map(int, line.split()))
        main_rows.append(row)
    
    # Collect all numbers except -1s
    all_numbers = []
    for row in main_rows:
        for num in row:
            if num != -1:
                all_numbers.append(num)
    
    # Sort the numbers
    all_numbers.sort()
    
    # Print the result
    print(' '.join(map(str, all_numbers)))

if __name__ == "__main__":
    main()
