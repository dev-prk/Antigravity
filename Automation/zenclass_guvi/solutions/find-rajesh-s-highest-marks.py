import sys

def main():
    # Read the first line containing the count of marks
    n = int(sys.stdin.readline().strip())
    
    # Read the second line containing the list of marks
    marks_line = sys.stdin.readline().strip()
    
    # Handle edge case where there might be no marks or empty input
    if not marks_line:
        print(-1)
        return
    
    # Parse the marks into a list of integers
    marks = list(map(int, marks_line.split()))
    
    # Handle edge case where the list is empty
    if not marks:
        print(-1)
        return
    
    # Find and print the maximum marks
    # Using built-in max function for O(n) time complexity
    print(max(marks))

if __name__ == "__main__":
    main()
