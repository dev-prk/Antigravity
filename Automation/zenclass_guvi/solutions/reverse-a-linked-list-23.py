class Node:
    def __init__(self, data):
        self.data = data
        self.next = None

def reverse_linked_list(head):
    prev = None
    current = head
    while current:
        next_node = current.next
        current.next = prev
        prev = current
        current = next_node
    return prev

def print_list(head):
    result = []
    while head:
        result.append(str(head.data))
        head = head.next
    print(' '.join(result))

def main():
    import sys
    n = int(sys.stdin.readline().strip())
    if n == 0:
        print()
        return
    data = list(map(int, sys.stdin.readline().split()))
    
    head = Node(data[0])
    current = head
    for i in range(1, n):
        current.next = Node(data[i])
        current = current.next
    
    reversed_head = reverse_linked_list(head)
    print_list(reversed_head)

if __name__ == "__main__":
    main()
