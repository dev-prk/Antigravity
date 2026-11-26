import sys
from collections import deque

class Node:
    __slots__ = ['val', 'left', 'right']
    def __init__(self, val):
        self.val = val
        self.left = None
        self.right = None

def main():
    line = sys.stdin.readline().strip()
    if not line:
        return
    tokens = line.split()
    nodes = {}
    
    i = 0
    while i < len(tokens):
        val = int(tokens[i])
        if val not in nodes:
            nodes[val] = Node(val)
        parent = nodes[val]
        i += 1
        if i >= len(tokens):
            break
        child_val = int(tokens[i])
        i += 1
        direction = tokens[i]
        i += 1
        if child_val not in nodes:
            nodes[child_val] = Node(child_val)
        child = nodes[child_val]
        if direction == 'L':
            parent.left = child
        else:
            parent.right = child
    
    root = None
    all_children = set()
    for val, node in nodes.items():
        if node.left:
            all_children.add(node.left.val)
        if node.right:
            all_children.add(node.right.val)
    for val in nodes:
        if val not in all_children:
            root = nodes[val]
            break
    
    result = []
    if root is None:
        print(' '.join(map(str, result)))
        return
    
    queue = deque([root])
    level = 0
    while queue:
        level_size = len(queue)
        current_level = []
        for _ in range(level_size):
            node = queue.popleft()
            current_level.append(node.val)
            if node.left:
                queue.append(node.left)
            if node.right:
                queue.append(node.right)
        if level % 2 == 1:
            current_level.reverse()
        result.extend(current_level)
        level += 1
    
    print(' '.join(map(str, result)))

if __name__ == "__main__":
    main()
