import sys

def delete_nth_from_end(head, n):
    if not head:
        return None
    
    dummy = ListNode(0)
    dummy.next = head
    first = dummy
    second = dummy
    
    for _ in range(n + 1):
        second = second.next
        if not second:
            return head
    
    while second:
        first = first.next
        second = second.next
    
    if first.next:
        first.next = first.next.next
    
    return dummy.next

class ListNode:
    def __init__(self, val=0):
        self.val = val
        self.next = None

def main():
    lines = sys.stdin.read().strip().split('\n')
    if len(lines) < 3:
        return
    
    size = int(lines[0].strip())
    values = list(map(int, lines[1].strip().split()))
    n = int(lines[2].strip())
    
    if size == 0 or n <= 0 or n > size:
        print(' '.join(map(str, values)))
        return
    
    head = ListNode(values[0])
    current = head
    for i in range(1, size):
        current.next = ListNode(values[i])
        current = current.next
    
    new_head = delete_nth_from_end(head, n)
    
    result = []
    while new_head:
        result.append(str(new_head.val))
        new_head = new_head.next
    
    print(' '.join(result))

if __name__ == "__main__":
    main()
