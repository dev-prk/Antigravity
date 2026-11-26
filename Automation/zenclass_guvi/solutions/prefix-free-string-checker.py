def main():
    import sys
    
    n = int(sys.stdin.readline().strip())
    strings = []
    for _ in range(n):
        strings.append(sys.stdin.readline().strip())
    
    # Build a trie
    class TrieNode:
        def __init__(self):
            self.children = {}
            self.is_end = False
    
    root = TrieNode()
    
    for i in range(n):
        s = strings[i]
        node = root
        
        for j, char in enumerate(s):
            # Check if current node marks end of a previous string
            # If so, this string is invalid (it has a prefix)
            if node.is_end:
                print("Bad input", s)
                return
            
            if char not in node.children:
                node.children[char] = TrieNode()
            node = node.children[char]
        
        # Check if current node already has children or is end of a string
        if node.is_end or len(node.children) > 0:
            print("Bad input", s)
            return
        
        # Mark this node as end of string
        node.is_end = True
    
    print("1000 Gold coins dispensed")

if __name__ == "__main__":
    main()
