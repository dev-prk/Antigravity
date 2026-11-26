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
    
    values = list(map(int, data[1:n+1]))
    
    class Node:
        def __init__(self, val):
            self.val = val
            self.left = None
            self.right = None
    
    def insert(root, val):
        if root is None:
            return Node(val)
        if val < root.val:
            root.left = insert(root.left, val)
        else:
            root.right = insert(root.right, val)
        return root
    
    def height(node):
        if node is None:
            return 0
        return 1 + max(height(node.left), height(node.right))
    
    root = None
    for val in values:
        root = insert(root, val)
    
    print(height(root))

if __name__ == "__main__":
    main()
