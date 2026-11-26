import sys

def main():
    # Read the first line (length of linked list)
    n_line = sys.stdin.readline()
    if not n_line:
        return
    n = int(n_line.strip())
    
    # Handle edge case of empty list
    if n == 0:
        print("")
        return
    
    # Read the second line (linked list data)
    data_line = sys.stdin.readline()
    data = list(map(int, data_line.split()))[:n]
    
    # Remove duplicates while preserving order
    seen = set()
    result = []
    for val in data:
        if val not in seen:
            seen.add(val)
            result.append(val)
    
    # Print the result
    print(' '.join(map(str, result)))

if __name__ == "__main__":
    main()
