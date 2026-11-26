import sys

def main():
    data = sys.stdin.read().strip().split()
    if not data:
        print(0)
        return
    
    n = int(data[0])
    
    if n == 0:
        print(0)
        return
    
    strings = data[1:n+1]
    prefix = data[n+1] if n + 1 < len(data) else ""
    
    count = 0
    prefix_len = len(prefix)
    
    for s in strings:
        if len(s) >= prefix_len and s.startswith(prefix):
            count += 1
    
    print(count)

if __name__ == "__main__":
    main()
