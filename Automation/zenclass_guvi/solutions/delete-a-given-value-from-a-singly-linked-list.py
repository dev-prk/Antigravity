import sys


class Node:
    __slots__ = ('data', 'next')

    def __init__(self, data):
        self.data = data
        self.next = None


def main():
    tokens = sys.stdin.read().split()
    if not tokens:
        return

    idx = 0
    n = int(tokens[idx])
    idx += 1

    values = []
    for _ in range(n):
        if idx < len(tokens):
            values.append(int(tokens[idx]))
            idx += 1

    x = int(tokens[idx]) if idx < len(tokens) else None

    head = None
    tail = None
    for v in values:
        node = Node(v)
        if head is None:
            head = node
            tail = node
        else:
            tail.next = node
            tail = node

    found = False

    if head is not None and head.data == x:
        head = head.next
        found = True
    else:
        curr = head
        while curr is not None and curr.next is not None:
            if curr.next.data == x:
                curr.next = curr.next.next
                found = True
                break
            curr = curr.next

    if not found:
        print("Value Not Found")
    else:
        parts = []
        curr = head
        while curr is not None:
            parts.append(str(curr.data))
            curr = curr.next
        print(" ".join(parts))


if __name__ == "__main__":
    main()
