import sys

def main():
    data = sys.stdin.read().strip().split()
    if not data:
        print("NO")
        return
    
    index = 0
    n = int(data[index])
    index += 1
    
    seen = set()
    
    for _ in range(n):
        if index >= len(data):
            print("NO")
            return
        m = int(data[index])
        index += 1
        
        if index + m > len(data):
            print("NO")
            return
            
        arr = tuple(int(data[index + i]) for i in range(m))
        index += m
        
        if arr in seen:
            print("YES")
            return
        seen.add(arr)
    
    print("NO")

if __name__ == "__main__":
    main()
