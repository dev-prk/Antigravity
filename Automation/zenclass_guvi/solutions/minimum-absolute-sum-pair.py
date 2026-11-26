import sys

def main():
    data = sys.stdin.read().strip().split()
    if not data:
        return
    
    n = int(data[0])
    if n == 0:
        return
    
    arr = list(map(int, data[1:n+1]))
    if n == 1:
        return
    
    arr.sort()
    
    left = 0
    right = n - 1
    best_sum = float('inf')
    result = (arr[0], arr[1])
    
    while left < right:
        current_sum = arr[left] + arr[right]
        abs_sum = abs(current_sum)
        
        if abs_sum < abs(best_sum):
            best_sum = current_sum
            result = (arr[left], arr[right])
        
        if current_sum < 0:
            left += 1
        elif current_sum > 0:
            right -= 1
        else:
            break
    
    # Sort result to ensure positive number comes first
    sorted_result = tuple(sorted(result))
    print(f"{sorted_result[0]} {sorted_result[1]}")

if __name__ == "__main__":
    main()
