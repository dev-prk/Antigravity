import sys

class Node:
    __slots__ = ('data', 'next')
    def __init__(self, data):
        self.data = data
        self.next = None

def main():
    tokens = sys.stdin.read().split()
    if not tokens:
        print("Sum: 0")
        return

    n = int(tokens[0])
    head = None
    tail = None

    for i in range(1, min(n, len(tokens) - 1) + 1):
        val = int(tokens[i])
        new_node = Node(val)
        if head is None:
            head = new_node
            tail = new_node
        else:
            tail.next = new_node
            tail = new_node

    total = 0
    curr = head
    while curr is not None:
        total += curr.data
        curr = curr.next

    print(f"Sum: {total}")

if __name__ == "__main__":
    main()
