import sys

class Node:
    def __init__(self, data):
        self.data = data
        self.left = None
        self.right = None

def insert(root, data):
    if root is None:
        return Node(data)
    if data < root.data:
        root.left = insert(root.left, data)
    elif data > root.data:
        root.right = insert(root.right, data)
    return root

def find_min(root):
    current = root
    while current.left is not None:
        current = current.left
    return current.data

def find_max(root):
    current = root
    while current.right is not None:
        current = current.right
    return current.data

def main():
    data = sys.stdin.read().strip().split()
    if not data:
        return
    n = int(data[0])
    if n == 0:
        return
    values = list(map(int, data[1:n+1]))
    root = None
    for val in values:
        root = insert(root, val)
    min_val = find_min(root)
    max_val = find_max(root)
    print(min_val)
    print(max_val)

if __name__ == "__main__":
    main()
