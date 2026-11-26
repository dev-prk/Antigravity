import sys

class TrieNode:
    __slots__ = ['children']
    def __init__(self):
        self.children = [None, None]

def main():
    data = sys.stdin.read().strip().split()
    if not data:
        return
    
    it = iter(data)
    n = int(next(it))
    q = int(next(it))
    arr = [int(next(it)) for _ in range(n)]
    queries = [int(next(it)) for _ in range(q)]
    
    root = TrieNode()
    
    for num in arr:
        node = root
        for b in range(30, -1, -1):
            bit = (num >> b) & 1
            if node.children[bit] is None:
                node.children[bit] = TrieNode()
            node = node.children[bit]
    
    results = []
    for x in queries:
        node = root
        max_xor = 0
        for b in range(30, -1, -1):
            bit = (x >> b) & 1
            toggled = 1 - bit
            if node.children[toggled] is not None:
                max_xor |= (1 << b)
                node = node.children[toggled]
            else:
                node = node.children[bit]
        results.append(max_xor)
    
    print('\n'.join(map(str, results)))

if __name__ == "__main__":
    main()
