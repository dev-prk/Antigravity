import sys

class Node:
    def __init__(self, data):
        self.data = data
        self.next = None

def main():
    lines = sys.stdin.read().strip().split('\n')
    if not lines:
        print("Not Found")
        return
    
    n = int(lines[0].strip())
    if n == 0:
        print("Not Found")
        return
    
    arr = list(map(int, lines[1].strip().split()))
    x = int(lines[2].strip())
    
    head = None
    tail = None
    
    for val in arr:
        new_node = Node(val)
        if head is None:
            head = new_node
            tail = new_node
        else:
            tail.next = new_node
            tail = new_node
    
    current = head
    found = False
    while current is not None:
        if current.data == x:
            found = True
            break
        current = current.next
    
    if found:
        print("Found")
    else:
        print("Not Found")

if __name__ == "__main__":
    main()
