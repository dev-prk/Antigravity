import sys
from collections import Counter

def solve():
    data = sys.stdin.read().strip().split()
    if not data:
        print("NO")
        return
    
    n = int(data[0])
    if n == 0:
        print("NO")
        return
    
    if n == 1:
        print("NO")
        return
    
    arr = data[1:n+1]
    count = Counter(arr)
    
    # Check if any element is palindromic itself (but we need two different elements)
    for num in arr:
        if num == num[::-1]:
            # Need to verify two different elements can be used
            if count[num] >= 2:
                # Can use same value from different positions
                for i in range(len(arr)):
                    for j in range(len(arr)):
                        if i != j and arr[i] == num and arr[j] == num:
                            concat = arr[i] + arr[j]
                            if concat == concat[::-1]:
                                print("YES")
                                return
    
    # Check pairs of different elements
    for i in range(len(arr)):
        for j in range(len(arr)):
            if i != j:
                concat = arr[i] + arr[j]
                if concat == concat[::-1]:
                    print("YES")
                    return
    
    print("NO")

if __name__ == "__main__":
    solve()
