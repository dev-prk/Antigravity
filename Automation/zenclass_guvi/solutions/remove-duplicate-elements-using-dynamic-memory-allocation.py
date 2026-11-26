class Node:
    def __init__(self, data, next=None):
        self.data = data
        self.next = next

def removeDuplicates(head):
    if head is None:
        return None, 0
    
    seen = {}
    unique_head = None
    unique_tail = None
    current = head
    
    while current is not None:
        if current.data not in seen:
            seen[current.data] = True
            new_node = Node(current.data)
            if unique_head is None:
                unique_head = new_node
                unique_tail = new_node
            else:
                unique_tail.next = new_node
                unique_tail = new_node
        current = current.next
    
    size = 0
    temp = unique_head
    while temp is not None:
        size += 1
        temp = temp.next
    
    return unique_head, size

def main():
    import sys
    data = sys.stdin.read().strip().split()
    if not data:
        return
    
    n = int(data[0])
    
    if n == 0:
        print("")
        return
    
    integers = list(map(int, data[1:n+1]))
    
    head = None
    tail = None
    
    for val in integers:
        new_node = Node(val)
        if head is None:
            head = new_node
            tail = new_node
        else:
            tail.next = new_node
            tail = new_node
    
    unique_head, new_size = removeDuplicates(head)
    
    result = []
    current = unique_head
    while current is not None:
        result.append(str(current.data))
        current = current.next
    
    print(" ".join(result))

if __name__ == "__main__":
    main()
