import sys

def main():
    data = sys.stdin.read().strip().split()
    if not data:
        print("0 0")
        return
    N = int(data[0])
    K = int(data[1])
    
    if N == 0 or K == 0:
        print("0 0")
        return
    
    if K == N:
        print("0 0")
        return
    
    available = N - K
    if available == 0:
        print("0 0")
        return
    
    # Maximum: place K inhabited as compact as possible, each covering 2 available
    if K == 1:
        max_good = min(2, available)
    else:
        max_good = min(2 * K, available)
    
    # Minimum: spread inhabited to minimize coverage
    # Place inhabited at ends and middle positions to minimize adjacent available
    # Optimal strategy: place all K occupied at one end
    if available <= 1:
        min_good = available
    else:
        # All K at one end leaves 'available' apartments
        # But only those adjacent to K are good (at most 2 for end placement)
        # Actually, if K at positions 1..K, then good are at K+1 if exists
        if K + 1 <= N:
            min_good = 1
        else:
            min_good = 0
        
        # But we need to be more careful
        # Minimum occurs when we minimize coverage of available apartments
        # Strategy: place all K occupied as compactly as possible
        # This leaves available consecutive apartments
        # Only the boundary ones are good
        
        if K + 1 <= N:
            # Available apartments from K+1 to N
            # Only K+1 is adjacent to K at position K
            # But wait, if K=1, then position 2 is good, and if N>2, positions 3..N are not good
            # So only 1 good apartment
            min_good = 1
        else:
            min_good = 0
    
    # More careful analysis for minimum:
    # Place all K occupied at one end (positions 1 to K)
    # Then available are positions K+1 to N
    # Only position K+1 is adjacent to K (at K)
    # So exactly 1 good if K < N
    
    min_good = 1 if K < N else 0
    
    print(f"{min_good} {max_good}")

if __name__ == "__main__":
    main()
