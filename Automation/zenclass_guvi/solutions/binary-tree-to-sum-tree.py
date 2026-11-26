import sys

class TreeNode:
    def __init__(self, val=0):
        self.val = val
        self.left = None
        self.right = None

def insert_into_bst(root, val):
    if root is None:
        return TreeNode(val)
    
    if val < root.val:
        root.left = insert_into_bst(root.left, val)
    else:
        root.right = insert_into_bst(root.right, val)
    
    return root

def build_bst_from_list(arr):
    if not arr:
        return None
    
    root = None
    for val in arr:
        root = insert_into_bst(root, val)
    
    return root

def convert_to_sum_tree(node):
    if node is None:
        return 0
    
    left_sum = convert_to_sum_tree(node.left)
    right_sum = convert_to_sum_tree(node.right)
    
    old_val = node.val
    node.val = left_sum + right_sum
    
    return old_val + left_sum + right_sum

def preorder_traversal(node):
    result = []
    if node is not None:
        result.append(str(node.val))
        result.extend(preorder_traversal(node.left))
        result.extend(preorder_traversal(node.right))
    return result

def main():
    data = sys.stdin.read().strip().split()
    if not data:
        return
    
    n = int(data[0])
    if n == 0:
        print("")
        return
    
    arr = list(map(int, data[1:n+1]))
    
    root = build_bst_from_list(arr)
    
    convert_to_sum_tree(root)
    
    result = preorder_traversal(root)
    
    print(" ".join(result))

if __name__ == "__main__":
    main()
