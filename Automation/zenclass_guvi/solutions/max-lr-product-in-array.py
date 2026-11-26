import sys

def main():
    data = sys.stdin.read().strip().split()
    if not data:
        print(0)
        return
    
    n = int(data[0])
    if n == 0:
        print(0)
        return
    
    arr = list(map(int, data[1:n+1]))
    
    # Arrays to store L(i) and R(i) (1-indexed)
    L = [0] * (n + 2)
    R = [0] * (n + 2)
    
    # Compute L array using stack
    stack = []
    for i in range(1, n + 1):
        while stack and arr[stack[-1] - 1] <= arr[i - 1]:
            stack.pop()
        if stack:
            L[i] = stack[-1]
        else:
            L[i] = 0
        stack.append(i)
    
    # Compute R array using stack
    stack = []
    for i in range(n, 0, -1):
        while stack and arr[stack[-1] - 1] <= arr[i - 1]:
            stack.pop()
        if stack:
            R[i] = stack[-1]
        else:
            R[i] = 0
        stack.append(i)
    
    # Calculate maximum LR product
    max_product = -1
    max_index = 0
    for i in range(1, n + 1):
        product = L[i] * R[i]
        if product > max_product:
            max_product = product
            max_index = i
        elif product == max_product:
            # If products are equal, we keep the first occurrence
            pass
    
    print(max_product)

if __name__ == "__main__":
    main()
