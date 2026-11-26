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

def find_height(root):
    if root is None:
        return -1
    left_height = find_height(root.left)
    right_height = find_height(root.right)
    return 1 + max(left_height, right_height)

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
    root = None
    for num in nums:
        root = insert(root, num)
    print(find_height(root))

if __name__ == "__main__":
    main()
