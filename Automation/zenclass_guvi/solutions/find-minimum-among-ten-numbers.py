import sys

def main():
    # Read the input line
    line = sys.stdin.readline()
    
    # Handle empty input
    if not line or not line.strip():
        print(-1)
        return
    
    # Split by spaces and convert to integers
    parts = line.split()
    numbers = []
    for part in parts:
        if part:  # Skip empty strings from multiple spaces
            numbers.append(int(part))
    
    # Handle case where we don't have exactly 10 numbers
    if len(numbers) != 10:
        print(-1)
        return
    
    # Find minimum
    min_val = numbers[0]
    for i in range(1, 10):
        if numbers[i] < min_val:
            min_val = numbers[i]
    
    print(min_val)

if __name__ == "__main__":
    main()
