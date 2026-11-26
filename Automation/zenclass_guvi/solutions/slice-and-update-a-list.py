import sys

def main():
    # Read the first line and parse integers
    line1 = sys.stdin.readline().strip()
    if not line1:
        return
    lst = list(map(int, line1.split()))
    
    # Read the second line for x
    x_line = sys.stdin.readline().strip()
    if not x_line:
        return
    x = int(x_line)
    
    # Print first three items
    print(lst[:3])
    
    # Print last three items
    print(lst[-3:])
    
    # Print every second item starting from first (index 0)
    print(lst[::2])
    
    # Add x, sort, and print final list
    lst.append(x)
    lst.sort()
    print(lst)

if __name__ == "__main__":
    main()
