import sys
sys.setrecursionlimit(100000)

def main():
    inorder = input().strip()
    postorder = input().strip()
    nodes = input().strip().split()
    u, v = nodes[0], nodes[1]

    if not inorder:
        print(-1)
        return

    in_idx = {ch: i for i, ch in enumerate(inorder)}

    def build_tree(in_start, in_end, post_start, post_end):
        if in_start > in_end or post_start > post_end:
            return None
        
        root_val = postorder[post_end]
        root = {'val': root_val, 'left': None, 'right': None}
        
        if in_start == in_end:
            return root
        
        idx = in_idx[root_val]
        left_size = idx - in_start
        
        root['left'] = build_tree(in_start, idx - 1, post_start, post_start + left_size - 1)
        root['right'] = build_tree(idx + 1, in_end, post_start + left_size, post_end - 1)
        
        return root

    root = build_tree(0, len(inorder) - 1, 0, len(postorder) - 1)

    def find_path(node, target):
        if not node:
            return None
        if node['val'] == target:
            return [node['val']]
        
        left_path = find_path(node['left'], target)
        if left_path:
            return [node['val']] + left_path
        
        right_path = find_path(node['right'], target)
        if right_path:
            return [node['val']] + right_path
        
        return None

    path_u = find_path(root, u)
    path_v = find_path(root, v)

    if not path_u or not path_v:
        print(-1)
        return

    i = 0
    while i < len(path_u) and i < len(path_v) and path_u[i] == path_v[i]:
        i += 1

    distance = (len(path_u) - i) + (len(path_v) - i)
    print(distance)

if __name__ == "__main__":
    main()
