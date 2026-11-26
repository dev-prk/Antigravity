import sys

def main():
    # Read all lines and strip them
    lines = [line.strip() for line in sys.stdin.readlines()]
    
    if not lines:
        return
    
    # Parse the size of the linked list
    n = int(lines[0])
    
    if n == 0 or len(lines) < 3:
        # Edge case: empty list or missing inputs
        print()
        return
    
    # Parse the linked list values
    values = list(map(int, lines[1].split()))
    
    # Parse the key to delete
    key = int(lines[2])
    
    if len(values) == 0:
        print()
        return
    
    # Find the last occurrence of the key
    last_index = -1
    for i in range(len(values) - 1, -1, -1):
        if values[i] == key:
            last_index = i
            break
    
    if last_index == -1:
        # Key not found, print original list
        print(' '.join(map(str, values)))
        return
    
    # Remove the last occurrence
    result = values[:last_index] + values[last_index + 1:]
    
    # Print the result
    print(' '.join(map(str, result)))

if __name__ == "__main__":
    main()
