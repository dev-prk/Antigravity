import sys

def main():
    # Read two lines from input
    line_a = sys.stdin.readline().strip()
    line_b = sys.stdin.readline().strip()
    
    # Handle empty lines
    if not line_a:
        a_set = set()
    else:
        a_list = list(map(int, line_a.split()))
        a_set = set(a_list)
    
    if not line_b:
        b_set = set()
    else:
        b_list = list(map(int, line_b.split()))
        b_set = set(b_list)
    
    # Compute set operations
    union = sorted(a_set | b_set)
    intersection = sorted(a_set & b_set)
    difference = sorted(a_set - b_set)
    
    # Print results in required format
    print(f"[{', '.join(map(str, union))}]")
    print(f"[{', '.join(map(str, intersection))}]")
    print(f"[{', '.join(map(str, difference))}]")

if __name__ == "__main__":
    main()
