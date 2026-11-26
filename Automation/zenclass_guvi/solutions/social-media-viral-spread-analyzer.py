import sys
from collections import deque

def bfs_reach_and_time(start, adj):
    visited = set()
    queue = deque([(start, 0)])
    visited.add(start)
    max_time = 0
    while queue:
        node, time = queue.popleft()
        max_time = max(max_time, time)
        for neighbor in adj.get(node, []):
            if neighbor not in visited:
                visited.add(neighbor)
                queue.append((neighbor, time + 1))
    return len(visited), max_time

def main():
    data = sys.stdin.read().strip().split()
    if not data:
        print("0 -1 -1")
        return
    idx = 0
    n = int(data[idx])
    idx += 1
    m = int(data[idx])
    idx += 1
    adj = {}
    users = set()
    for _ in range(m):
        u = int(data[idx])
        idx += 1
        v = int(data[idx])
        idx += 1
        users.add(u)
        users.add(v)
        if u not in adj:
            adj[u] = []
        adj[u].append(v)
    start_user = int(data[idx])
    idx += 1
    all_users = users if users else {start_user}
    total_reach, time_to_viral = bfs_reach_and_time(start_user, adj)
    max_influence = 0
    most_influential_user = -1
    sorted_users = sorted(all_users)
    for user in sorted_users:
        reach, _ = bfs_reach_and_time(user, adj)
        if reach > max_influence:
            max_influence = reach
            most_influential_user = user
        elif reach == max_influence and most_influential_user != -1 and user < most_influential_user:
            most_influential_user = user
    print(f"{total_reach} {time_to_viral} {most_influential_user}")

if __name__ == "__main__":
    main()
