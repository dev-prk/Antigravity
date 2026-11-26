import sys

def main():
    data = sys.stdin.read().split()
    if not data:
        return
    try:
        n = int(data[0])
    except ValueError:
        n = 0
    if n <= 0:
        print("")
        return
    values = []
    for i in range(1, min(n, len(data) - 1) + 1):
        try:
            values.append(int(data[i]))
        except ValueError:
            values.append(data[i])

    class Node:
        __slots__ = ('data', 'next')
        def __init__(self, val):
            self.data = val
            self.next = None

    if values:
        head = Node(values[0])
        tail = head
        for v in values[1:]:
            node = Node(v)
            tail.next = node
            tail = node

        out = []
        cur = head
        while cur is not None:
            out.append(str(cur.data))
            cur = cur.next
        print(" ".join(out) + " ")
    else:
        print("")

if __name__ == "__main__":
    main()
