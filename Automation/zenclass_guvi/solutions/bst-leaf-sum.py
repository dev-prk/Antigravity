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
    
    if n == 1:
        print(arr[0])
        return
    
    class Node:
        def __init__(self, val):
            self.val = val
            self.left = None
            self.right = None
    
    root = Node(arr[0])
    
    for val in arr[1:]:
        current = root
        while True:
            if val < current.val:
                if current.left is None:
                    current.left = Node(val)
                    break
                else:
                    current = current.left
            else:
                if current.right is None:
                    current.right = Node(val)
                    break
                else:
                    current = current.right
    
    leaf_sum = 0
    stack = [root]
    
    while stack:
        node = stack.pop()
        if node.left is None and node.right is None:
            leaf_sum += node.val
        else:
            if node.right:
                stack.append(node.right)
            if node.left:
                stack.append(node.left)
    
    print(leaf_sum)

if __name__ == "__main__":
    main()
