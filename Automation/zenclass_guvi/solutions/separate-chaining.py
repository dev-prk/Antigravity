import sys

def main():
    data = sys.stdin.read().strip().split()
    if not data:
        return
    
    n = int(data[0])
    m = int(data[1])
    
    keys = list(map(int, data[2:2+m]))
    
    table = [[] for _ in range(n)]
    
    for key in keys:
        bucket_index = key % n
        table[bucket_index].append(key)
    
    for i in range(n):
        if table[i]:
            print(f"{i}: " + " ".join(map(str, table[i])))
        else:
            print(f"{i}:")

if __name__ == "__main__":
    main()
