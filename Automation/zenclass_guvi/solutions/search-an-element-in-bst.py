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

def search(root, key):
    if root is None or root.data == key:
        return root is not None
    if key < root.data:
        return search(root.left, key)
    return search(root.right, key)

def main():
    data = sys.stdin.read().strip().split()
    if not data:
        return
    idx = 0
    n = int(data[idx])
    idx += 1
    root = None
    for _ in range(n):
        val = int(data[idx])
        idx += 1
        root = insert(root, val)
    key = int(data[idx])
    if search(root, key):
        print("Found")
    else:
        print("Not Found")

if __name__ == "__main__":
    main()
