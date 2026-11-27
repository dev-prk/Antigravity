import sys

class Node:
    def __init__(self, name, duration):
        self.name = name
        self.duration = duration
        self.prev = None
        self.next = None

def main():
    Q = int(sys.stdin.readline().strip())
    head = None
    tail = None
    current = None
    
    for _ in range(Q):
        line = sys.stdin.readline().strip()
        parts = line.split()
        op = parts[0]
        
        if op == "PUSH":
            name = parts[1]
            duration = int(parts[2])
            new_node = Node(name, duration)
            if head is None:
                head = new_node
                tail = new_node
                current = new_node
            else:
                tail.next = new_node
                new_node.prev = tail
                tail = new_node
        
        elif op == "REMOVE":
            name = parts[1]
            found = False
            temp = head
            while temp:
                if temp.name == name:
                    found = True
                    if temp == head and temp == tail:
                        head = None
                        tail = None
                        current = None
                    elif temp == head:
                        head = head.next
                        head.prev = None
                        if current == temp:
                            current = head
                    elif temp == tail:
                        tail = tail.prev
                        tail.next = None
                        if current == temp:
                            current = tail
                    else:
                        temp.prev.next = temp.next
                        temp.next.prev = temp.prev
                        if current == temp:
                            current = temp.next
                    break
                temp = temp.next
            
            if not found:
                sys.stdout.write("Track not found\n")
        
        elif op == "FORWARD":
            if current and current.next:
                current = current.next
            else:
                sys.stdout.write("No forward track\n")
        
        elif op == "BACK":
            if current and current.prev:
                current = current.prev
            else:
                sys.stdout.write("No backward track\n")
        
        elif op == "SHOW":
            output = []
            temp = current
            while temp:
                output.append(temp.name)
                temp = temp.next
            sys.stdout.write(" ".join(output))
            if output:
                sys.stdout.write(" ")
            sys.stdout.write("\n")

if __name__ == "__main__":
    main()
