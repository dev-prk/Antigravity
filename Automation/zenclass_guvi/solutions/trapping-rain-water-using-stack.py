import sys

def trap_rain_water(heights):
    if not heights:
        return 0
    
    n = len(heights)
    stack = []
    water = 0
    
    for i in range(n):
        while stack and heights[i] > heights[stack[-1]]:
            top = stack.pop()
            
            if not stack:
                break
            
            left_bound = stack[-1]
            width = i - left_bound - 1
            height = min(heights[i], heights[left_bound]) - heights[top]
            water += width * height
        
        stack.append(i)
    
    return water

def main():
    data = sys.stdin.read().strip().split()
    if not data:
        print(0)
        return
    
    n = int(data[0])
    
    if n == 0:
        print(0)
        return
    
    heights = list(map(int, data[1:1+n]))
    
    result = trap_rain_water(heights)
    print(result)

if __name__ == "__main__":
    main()
