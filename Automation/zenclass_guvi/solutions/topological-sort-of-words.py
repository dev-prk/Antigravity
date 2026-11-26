import sys
from collections import defaultdict, deque

def topological_sort(words):
    # Build adjacency list and in-degree map
    graph = defaultdict(set)
    in_degree = defaultdict(int)
    chars = set()
    
    # Extract all characters
    for word in words:
        for c in word:
            chars.add(c)
    
    # Build graph from consecutive word pairs
    for i in range(len(words) - 1):
        w1, w2 = words[i], words[i + 1]
        min_len = min(len(w1), len(w2))
        found = False
        for j in range(min_len):
            if w1[j] != w2[j]:
                # Found ordering constraint
                if w2[j] not in graph[w1[j]]:
                    graph[w1[j]].add(w2[j])
                    in_degree[w2[j]] += 1
                found = True
                break
        # If no difference found and w1 is longer prefix of w2, invalid
        if not found and len(w1) > len(w2):
            return "-1"
    
    # Initialize in-degrees for all chars (those with 0 in-degree)
    for c in chars:
        if c not in in_degree:
            in_degree[c] = 0
    
    # Kahn's algorithm with BFS using deque for efficiency
    queue = deque()
    for c in chars:
        if in_degree[c] == 0:
            queue.append(c)
    
    result = []
    while queue:
        # Sort to ensure deterministic order when multiple choices
        queue = deque(sorted(queue))
        curr = queue.popleft()
        result.append(curr)
        for neighbor in sorted(graph[curr]):
            in_degree[neighbor] -= 1
            if in_degree[neighbor] == 0:
                queue.append(neighbor)
    
    # Check if topological sort is possible (no cycles)
    if len(result) != len(chars):
        return "-1"
    
    return "".join(result)

def main():
    s = sys.stdin.readline().strip()
    if not s:
        print("")
        return
    words = s.split()
    result = topological_sort(words)
    print(result)

if __name__ == "__main__":
    main()
