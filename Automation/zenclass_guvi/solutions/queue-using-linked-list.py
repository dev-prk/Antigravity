import sys

class Node:
    def __init__(self, data):
        self.data = data
        self.next = None

def main():
    data = sys.stdin.read().strip().split()
    if not data:
        return
    
    idx = 0
    N = int(data[idx])
    idx += 1
    
    if N > 0:
        elements = list(map(int, data[idx:idx+N]))
        idx += N
    else:
        elements = []
    
    if idx < len(data):
        O = int(data[idx])
        idx += 1
        if O == 1:
            X = int(data[idx])
            idx += 1
        else:
            X = None
    else:
        O = 0
        X = None
    
    if not elements:
        if O == 1:
            print(X)
        else:
            print(-1)
        return
    
    head = Node(elements[0])
    current = head
    for i in range(1, len(elements)):
        current.next = Node(elements[i])
        current = current.next
    tail = current
    
    if O == 1:
        new_node = Node(X)
        tail.next = new_node
        tail = new_node
    elif O == 2:
        if head is None:
            print(-1)
            return
        else:
            head = head.next
            if head is None:
                tail = None
    
    result = []
    current = head
    while current is not None:
        result.append(str(current.data))
        current = current.next
    
    print(' '.join(result))

if __name__ == "__main__":
    main()
