import sys

def solve():
    data = sys.stdin.read().strip().split()
    if not data:
        print(-1)
        return
    
    n = int(data[0])
    if n == 0:
        print(-1)
        return
    
    arr = list(map(int, data[1:n+1]))
    
    if n == 1:
        print(-1)
        return
    
    # Find all indices where arr[i] > arr[i+1]
    violations = []
    for i in range(n - 1):
        if arr[i] > arr[i + 1]:
            violations.append(i)
    
    # If no violations, array is already sorted
    if not violations:
        print(-1)
        return
    
    # If more than one violation, need more than one update
    if len(violations) > 1:
        print(-1)
        return
    
    # Single violation at index i
    i = violations[0]
    
    # Try changing arr[i] to fix the array
    # Original violation: arr[i] > arr[i+1]
    # After change, we need arr[i] <= arr[i+1]
    
    # Option 1: Change arr[i] to arr[i+1]
    # Check if arr[i-1] <= arr[i+1] (if i > 0)
    # And arr[i+1] <= arr[i+2] (if i+2 < n) - but arr[i+1] <= arr[i+2] was already checked since no other violations
    
    # Option 2: Change arr[i+1] to arr[i]
    # Check if arr[i] <= arr[i+2] (if i+2 < n) - already checked
    # And arr[i-1] <= arr[i] (if i > 0)
    
    # Check option 1: change arr[i] to arr[i+1]
    valid1 = True
    if i > 0 and arr[i-1] > arr[i+1]:
        valid1 = False
    
    # Check option 2: change arr[i+1] to arr[i]
    valid2 = True
    if i + 2 < n and arr[i] > arr[i+2]:
        valid2 = False
    
    if valid1 and valid2:
        # Both options work, return the left index
        print(i)
    elif valid1:
        print(i)
    elif valid2:
        print(i + 1)
    else:
        print(-1)

if __name__ == "__main__":
    solve()
