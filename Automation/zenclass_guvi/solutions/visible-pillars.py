import sys

def main():
    data = sys.stdin.read().strip().split()
    if not data:
        return
    n = int(data[0])
    heights = list(map(int, data[1:1+n]))
    
    if n == 0:
        print(0)
        return
    
    max_height = heights[0]
    count = 1
    
    for i in range(1, n):
        if heights[i] > max_height:
            count += 1
            max_height = heights[i]
    
    print(count)

if __name__ == "__main__":
    main()
