class Node:
    def __init__(self, data):
        self.data = data
        self.next = None

def count_nodes(head):
    count = 0
    current = head
    while current:
        count += 1
        current = current.next
    return count

def main():
    import sys
    data = sys.stdin.read().strip().split()
    if not data:
        print("Node Count: 0")
        return
    
    n = int(data[0])
    if n == 0 or len(data) < 1:
        print("Node Count: 0")
        return
    
    elements = list(map(int, data[1:n+1]))
    
    if not elements:
        print("Node Count: 0")
        return
    
    head = Node(elements[0])
    current = head
    for i in range(1, len(elements)):
        current.next = Node(elements[i])
        current = current.next
    
    count = count_nodes(head)
    print(f"Node Count: {count}")

if __name__ == "__main__":
    main()
