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

def find_max(root):
    if root is None:
        return -1
    while root.right is not None:
        root = root.right
    return root.data

def main():
    lines = sys.stdin.read().strip().split()
    if not lines:
        print(-1)
        return
    n = int(lines[0])
    if n == 0:
        print(-1)
        return
    values = list(map(int, lines[1:1+n]))
    root = None
    for val in values:
        root = insert(root, val)
    print(find_max(root))

if __name__ == "__main__":
    main()
