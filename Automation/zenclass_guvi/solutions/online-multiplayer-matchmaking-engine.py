import sys

def solve():
    data = sys.stdin.read().split()
    if not data:
        return
    idx = 0
    n = int(data[idx]); idx += 1
    k = int(data[idx]); idx += 1
    skills = []
    for i in range(n):
        skills.append(int(data[idx])); idx += 1
    
    skills.sort()
    
    # Greedy: try to match smallest available player with the next one that fits
    i = 0
    matches = 0
    while i < n - 1:
        if skills[i + 1] - skills[i] <= k:
            matches += 1
            i += 2
        else:
            i += 1
    print(matches)

solve()
