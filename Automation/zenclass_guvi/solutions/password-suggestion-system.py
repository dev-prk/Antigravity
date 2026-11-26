import sys
from bisect import bisect_right

class Trie:
    def __init__(self):
        self.children = {}
        self.count = 0  # Number of passwords ending at this node
        self.end = False  # Is this the end of a password?

def main():
    # Read number of existing passwords
    N = int(sys.stdin.readline().strip())
    
    # Build the trie with existing passwords
    trie = Trie()
    words = set()  # Keep track of all existing passwords
    
    for _ in range(N):
        word = sys.stdin.readline().strip()
        words.add(word)
        node = trie
        for char in word:
            if char not in node.children:
                node.children[char] = Trie()
            node = node.children[char]
        node.end = True
        node.count += 1
    
    # Read number of queries
    Q = int(sys.stdin.readline().strip())
    
    results = []
    
    for _ in range(Q):
        password = sys.stdin.readline().strip()
        
        if password not in words:
            # Password doesn't exist, use it as is
            words.add(password)
            node = trie
            for char in password:
                if char not in node.children:
                    node.children[char] = Trie()
                node = node.children[char]
            node.end = True
            node.count += 1
            results.append(password)
        else:
            # Password exists, find lexicographically smallest greater password
            new_pass = find_next_password(trie, password)
            words.add(new_pass)
            node = trie
            for char in new_pass:
                if char not in node.children:
                    node.children[char] = Trie()
                node = node.children[char]
            node.end = True
            node.count += 1
            results.append(new_pass)
    
    for result in results:
        print(result)

def find_next_password(trie, password):
    """
    Find the lexicographically smallest password that is greater than
    the given password and doesn't already exist.
    """
    # First, try to find a simple increment (e.g., abcd -> abcd1)
    current_num = 0
    base = password
    
    # Check if there's a number at the end
    i = len(password) - 1
    while i >= 0 and password[i].isdigit():
        i -= 1
    
    if i < len(password) - 1:
        # There's a number at the end
        base = password[:i+1]
        num_str = password[i+1:]
        try:
            current_num = int(num_str)
        except:
            current_num = 0
    
    # Try incrementing the number
    candidate = base + str(current_num + 1)
    temp_trie = trie
    found = True
    node = temp_trie
    for char in candidate:
        if char not in node.children:
            found = False
            break
        node = node.children[char]
    
    if not found or (not node.end):
        return candidate
    
    # If that doesn't work (it already exists), try base + "1"
    candidate = base + "1"
    node = trie
    for char in candidate:
        if char not in node.children:
            return candidate
        node = node.children[char]
    
    # If candidate ends at a password node, try base + "2", etc.
    suffix = 1
    while True:
        candidate = base + str(suffix)
        node = trie
        valid = True
        for char in candidate:
            if char not in node.children:
                return candidate
            node = node.children[char]
        
        # Check if this path leads to a complete password
        if not node.end:
            return candidate
        
        suffix += 1

if __name__ == "__main__":
    main()
