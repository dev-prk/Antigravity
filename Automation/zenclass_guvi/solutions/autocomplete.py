import sys
from collections import defaultdict

def main():
    data = sys.stdin.read().splitlines()
    if not data:
        return
    
    idx = 0
    n = int(data[idx])
    idx += 1
    
    words = []
    for _ in range(n):
        words.append(data[idx])
        idx += 1
    
    prefix_dict = defaultdict(list)
    for word in words:
        for i in range(len(word) + 1):
            prefix = word[:i]
            prefix_dict[prefix].append(word)
    
    for prefix in prefix_dict:
        prefix_dict[prefix] = sorted(set(prefix_dict[prefix]))
    
    q = int(data[idx])
    idx += 1
    
    results = []
    for _ in range(q):
        s = data[idx]
        idx += 1
        
        if s not in prefix_dict:
            results.append(s)
        else:
            candidates = prefix_dict[s]
            # Filter candidates to only those that start with s
            valid_candidates = [c for c in candidates if c.startswith(s)]
            
            if len(valid_candidates) == 0:
                results.append(s)
            elif len(valid_candidates) == 1:
                results.append(valid_candidates[0])
            else:
                results.append(valid_candidates[0] + "+")
    
    for result in results:
        print(result)

if __name__ == "__main__":
    main()
