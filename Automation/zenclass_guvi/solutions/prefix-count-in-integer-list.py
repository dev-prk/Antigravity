import sys

def main():
    class TrieNode:
        __slots__ = ['count', 'children']
        def __init__(self):
            self.count = 0
            self.children = {}

    class Trie:
        def __init__(self):
            self.root = TrieNode()

        def insert(self, word):
            node = self.root
            for char in word:
                if char not in node.children:
                    node.children[char] = TrieNode()
                node = node.children[char]
                node.count += 1

        def get_count(self, prefix):
            node = self.root
            for char in prefix:
                if char not in node.children:
                    return 0
                node = node.children[char]
            return node.count

    def main():
        input = sys.stdin.read().split()
        ptr = 0

        N = int(input[ptr])
        ptr += 1

        numbers = []
        for _ in range(N):
            num = int(input[ptr])
            ptr += 1
            numbers.append(num)

        Q = int(input[ptr])
        ptr += 1

        queries = []
        for _ in range(Q):
            X = input[ptr]
            ptr += 1
            queries.append(X)

        trie = Trie()
        for num in numbers:
            num_str = str(num)
            trie.insert(num_str)

        output = []
        for query in queries:
            count = trie.get_count(query)
            output.append(str(count))

        print('\n'.join(output))

    if __name__ == "__main__":
        main()

if __name__ == "__main__":
    main()
