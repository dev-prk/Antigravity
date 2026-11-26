import sys

def main():
    # Read three strings from stdin
    s1 = sys.stdin.readline().rstrip('\n')
    s2 = sys.stdin.readline().rstrip('\n')
    s3 = sys.stdin.readline().rstrip('\n')
    
    # Display in original order
    print(f"Original Order: {s1} {s2} {s3}")
    
    # Display in reverse order
    print(f"Reverse Order: {s3} {s2} {s1}")
    
    # Concatenate all strings
    combined = s1 + s2 + s3
    print(f"Combined: {combined}")
    
    # Display total number of characters
    print(f"Total Characters: {len(combined)}")

if __name__ == "__main__":
    main()
