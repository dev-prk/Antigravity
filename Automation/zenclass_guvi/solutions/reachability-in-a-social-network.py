import sys
from collections import deque

def main():
    # Read number of members
    n = int(sys.stdin.readline().strip())
    
    # Read member IDs
    members = []
    for _ in range(n):
        members.append(int(sys.stdin.readline().strip()))
    
    # Create a set of member IDs for O(1) lookup
    member_set = set(members)
    
    # Read number of edges
    e = int(sys.stdin.readline().strip())
    
    # Build adjacency list
    adj = {m: [] for m in members}
    for _ in range(e):
        line = sys.stdin.readline().strip()
        follower, following = map(int, line.split())
        if follower in member_set and following in member_set:
            adj[follower].append(following)
    
    # Read source and destination
    source = int(sys.stdin.readline().strip())
    dest = int(sys.stdin.readline().strip())
    
    # Check if source and destination are valid members
    if source not in member_set or dest not in member_set:
        print(0)
        return
    
    # BFS to check reachability
    visited = set()
    queue = deque([source])
    visited.add(source)
    
    while queue:
        node = queue.popleft()
        if node == dest:
            print(1)
            return
        for neighbor in adj[node]:
            if neighbor not in visited:
                visited.add(neighbor)
                queue.append(neighbor)
    
    print(0)

if __name__ == "__main__":
    main()
