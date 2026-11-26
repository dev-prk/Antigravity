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

def inorder(root, result):
    if root:
        inorder(root.left, result)
        result.append(root.data)
        inorder(root.right, result)

def main():
    data = sys.stdin.read().strip().split()
    if not data:
        return
    n = int(data[0])
    if n == 0:
        print(-1)
        return
    values = list(map(int, data[1:n+1]))
    root = None
    for val in values:
        if val not in [v for v in values[:values.index(val)]]:
            root = insert(root, val)
        else:
            pass
    root = None
    for val in values:
        root = insert(root, val)
    result = []
    inorder(root, result)
    print(' '.join(map(str, result)))

if __name__ == "__main__":
    main()
