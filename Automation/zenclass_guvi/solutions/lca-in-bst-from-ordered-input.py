from sys import stdin

def main():
    data = list(map(int, stdin.read().split()))
    if not data:
        return
    idx = 0
    n = data[idx]
    idx += 1
    if n == 0:
        print(-1)
        return
    nums = data[idx:idx+n]
    idx += n
    if idx+2 > len(data):
        print(-1)
        return
    u = data[idx]
    v = data[idx+1]
    root = None
    class Node:
        __slots__ = ['val', 'left', 'right']
        def __init__(self, val):
            self.val = val
            self.left = None
            self.right = None
    for val in nums:
        new_node = Node(val)
        if root is None:
            root = new_node
        else:
            cur = root
            while True:
                if val < cur.val:
                    if cur.left is None:
                        cur.left = new_node
                        break
                    cur = cur.left
                else:
                    if cur.right is None:
                        cur.right = new_node
                        break
                    cur = cur.right
    def find_lca(node, u, v):
        if node is None:
            return -1
        if u < node.val and v < node.val:
            return find_lca(node.left, u, v)
        if u > node.val and v > node.val:
            return find_lca(node.right, u, v)
        return node.val
    res = find_lca(root, u, v)
    print(res if res is not None else -1)

if __name__ == "__main__":
    main()
