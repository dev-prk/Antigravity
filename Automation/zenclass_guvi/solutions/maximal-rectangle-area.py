import sys

def largest_rectangle(heights):
    stack = []
    max_area = 0
    n = len(heights)
    for i in range(n + 1):
        h = heights[i] if i < n else 0
        while stack and h < heights[stack[-1]]:
            height = heights[stack.pop()]
            width = i if not stack else i - stack[-1] - 1
            max_area = max(max_area, height * width)
        stack.append(i)
    return max_area

def main():
    data = sys.stdin.read().strip().split()
    if not data:
        print(0)
        return
    it = iter(data)
    a = int(next(it))
    b = int(next(it))
    total = a * b
    matrix = [0] * total
    for i in range(total):
        matrix[i] = int(next(it))
    if a == 0 or b == 0:
        print(0)
        return
    heights = [0] * b
    max_area = 0
    for val in matrix:
        if val == 1:
            heights[val // b if b != 0 else 0]  # This line is wrong; need correct indexing
    # Correct approach:
    idx = 0
    for i in range(a):
        for j in range(b):
            if matrix[idx] == 1:
                heights[j] += 1
            else:
                heights[j] = 0
            idx += 1
        max_area = max(max_area, largest_rectangle(heights))
    print(max_area)

if __name__ == "__main__":
    main()
