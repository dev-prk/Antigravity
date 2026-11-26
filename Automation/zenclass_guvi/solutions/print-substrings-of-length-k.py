import sys

def main():
    # Read the entire input and split by whitespace
    data = sys.stdin.read().strip().split()
    
    if len(data) < 2:
        return
    
    # The string is the first element, K is the second
    S = data[0]
    try:
        K = int(data[1])
    except ValueError:
        return
    
    # Handle edge cases
    if K <= 0 or len(S) < K:
        return
    
    # Generate all substrings of length K
    substrings = []
    for i in range(len(S) - K + 1):
        substrings.append(S[i:i+K])
    
    # Print space-separated
    print(' '.join(substrings))

if __name__ == "__main__":
    main()
