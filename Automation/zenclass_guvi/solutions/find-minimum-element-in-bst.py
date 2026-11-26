import sys

class Node:
    def __init__(self, value):
        self.val = value
        self.left = None
        self.right = None

def insert(root, value):
    if root is None:
        return Node(value)
    if value < root.val:
        root.left = insert(root.left, value)
    else:
        root.right = insert(root.right, value)
    return root

def find_minimum(root):
    if root is None:
        return None
    current = root
    while current.left is not None:
        current = current.left
    return current.val

def main():
    data = sys.stdin.read().strip().split()
    if not data:
        print(-1)
        return
    n = int(data[0])
    if n == 0:
        print(-1)
        return
    nums = list(map(int, data[1:n+1]))
    if not nums:
        print(-1)
        return
    root = None
    for num in nums:
        root = insert(root, num)
    min_val = find_minimum(root)
    if min_val is None:
        print(-1)
    else:
        print(min_val)

if __name__ == "__main__":
    main()
