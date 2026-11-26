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
    
    jobs = []
    idx = 1
    max_deadline = 0
    
    for i in range(n):
        job_id = int(data[idx])
        deadline = int(data[idx + 1])
        profit = int(data[idx + 2])
        jobs.append((profit, deadline, job_id))
        max_deadline = max(max_deadline, deadline)
        idx += 3
    
    jobs.sort(reverse=True)
    
    parent = list(range(max_deadline + 1))
    
    def find(x):
        if parent[x] != x:
            parent[x] = find(parent[x])
        return parent[x]
    
    total_profit = 0
    
    for profit, deadline, job_id in jobs:
        slot = find(deadline)
        if slot > 0:
            total_profit += profit
            parent[slot] = slot - 1
    
    print(total_profit)

if __name__ == "__main__":
    main()
