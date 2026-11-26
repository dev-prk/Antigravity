import sys

def main():
    data = sys.stdin.read().splitlines()
    if not data:
        return
    
    idx = 0
    N = int(data[idx])
    idx += 1
    
    words = []
    for _ in range(N):
        words.append(data[idx])
        idx += 1
    
    Q = int(data[idx])
    idx += 1
    
    words.sort()  # Sort to find lexicographically smallest
    
    for _ in range(Q):
        query = data[idx]
        idx += 1
        
        found = query  # Default: return query as is
        for word in words:
            if word.startswith(query):
                found = word
                break
        
        print(found)

if __name__ == "__main__":
    main()
