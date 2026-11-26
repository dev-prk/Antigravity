import sys

class TrieNode:
    def __init__(self):
        self.children = {}
        self.is_end = False
        self.has_prefix = False

def main():
    data = sys.stdin.read().splitlines()
    if not data:
        return
    
    idx = 0
    n = int(data[idx])
    idx += 1
    
    passwords = []
    for _ in range(n):
        passwords.append(data[idx].strip())
        idx += 1
    
    # Build the trie
    root = TrieNode()
    for pwd in passwords:
        node = root
        for char in pwd:
            if char not in node.children:
                node.children[char] = TrieNode()
            node = node.children[char]
            node.has_prefix = True
        node.is_end = True
    
    q = int(data[idx])
    idx += 1
    
    results = []
    for _ in range(q):
        new_pwd = data[idx].strip()
        idx += 1
        
        node = root
        is_valid = True
        for char in new_pwd:
            if char not in node.children:
                break
            node = node.children[char]
            if node.is_end:
                is_valid = False
                break
        else:
            # Check if new password has any existing password as prefix
            if node.has_prefix and node != root:
                is_valid = False
        
        if is_valid:
            results.append("Allowed")
        else:
            results.append("Invalid")
    
    print('\n'.join(results))

if __name__ == "__main__":
    main()
