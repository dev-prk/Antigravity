import sys

class Node:
    def __init__(self, reg_no, name, marks):
        self.reg_no = reg_no
        self.name = name
        self.marks = marks
        self.next = None

def main():
    data = sys.stdin.read().strip().split('\n')
    if not data:
        return
    
    n = int(data[0].strip())
    
    if n == 0:
        print("Student Deleted Successfully")
        print("Remaining Students:")
        return
    
    head = None
    tail = None
    
    for i in range(1, n + 1):
        parts = data[i].strip().split()
        if len(parts) >= 3:
            reg_no = int(parts[0])
            name = parts[1]
            marks = int(parts[2])
            new_node = Node(reg_no, name, marks)
            if head is None:
                head = new_node
                tail = new_node
            else:
                tail.next = new_node
                tail = new_node
    
    del_reg = int(data[n + 1].strip()) if n + 1 < len(data) else -1
    
    # Delete node with given register number
    if head is not None:
        if head.reg_no == del_reg:
            head = head.next
        else:
            prev = head
            curr = head.next
            found = False
            while curr is not None:
                if curr.reg_no == del_reg:
                    prev.next = curr.next
                    found = True
                    break
                prev = curr
                curr = curr.next
    
    print("Student Deleted Successfully")
    print("Remaining Students:")
    current = head
    while current is not None:
        print(f"{current.reg_no} {current.name} {current.marks}")
        next_node = current.next
        current = next_node

if __name__ == "__main__":
    main()
