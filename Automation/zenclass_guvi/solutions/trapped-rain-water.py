import sys

def trap_rain_water(heights):
    if not heights:
        return 0
    
    n = len(heights)
    if n <= 2:
        return 0
    
    # Two-pointer approach
    left = 0
    right = n - 1
    left_max = 0
    right_max = 0
    water = 0
    
    while left <= right:
        if heights[left] <= heights[right]:
            if heights[left] >= left_max:
                left_max = heights[left]
            else:
                water += left_max - heights[left]
            left += 1
        else:
            if heights[right] >= right_max:
                right_max = heights[right]
            else:
                water += right_max - heights[right]
            right -= 1
    
    return water

def main():
    lines = sys.stdin.read().strip().split('\n')
    if not lines:
        return
    
    n = int(lines[0].strip())
    if len(lines) < 2 or n == 0:
        print(0)
        return
    
    heights = list(map(int, lines[1].strip().split()))
    result = trap_rain_water(heights)
    print(result)

if __name__ == "__main__":
    main()
