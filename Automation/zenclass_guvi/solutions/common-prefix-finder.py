import sys
from collections import defaultdict

def main():
    # Read number of strings
    n = int(sys.stdin.readline().strip())
    
    # Read the n strings
    strings = []
    for _ in range(n):
        s = sys.stdin.readline().strip()
        strings.append(s)
    
    # Build a trie-like dictionary: prefix -> list of strings
    prefix_dict = defaultdict(list)
    
    for s in strings:
        # Add all prefixes of this string to the dictionary
        for i in range(1, len(s) + 1):
            prefix = s[:i]
            prefix_dict[prefix].append(s)
    
    # Read number of queries
    q = int(sys.stdin.readline().strip())
    
    # Process each query
    output_lines = []
    for _ in range(q):
        prefix = sys.stdin.readline().strip()
        if prefix in prefix_dict:
            # Join all strings with this prefix
            result = ' '.join(prefix_dict[prefix])
            output_lines.append(result)
        else:
            output_lines.append("No strings for query")
    
    # Print all results
    for line in output_lines:
        print(line)

if __name__ == "__main__":
    main()
