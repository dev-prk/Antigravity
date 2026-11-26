import sys

def main():
    line = sys.stdin.readline().strip()
    
    # Parse p=[...]
    if line.startswith('p=['):
        end_bracket = line.find(']')
        p_str = line[3:end_bracket]
        p = [int(x.strip()) for x in p_str.split(',')]
        
        # Find k=
        k_start = line.find('k=')
        k_part = line[k_start + 2:]
        k = int(k_part)
    else:
        return
    
    n = len(p)
    
    # Handle empty permutation
    if n == 0:
        print('[]')
        return
    
    # Build inverse permutation (1-indexed)
    inv = [0] * (n + 1)
    for i in range(n):
        inv[p[i]] = i + 1
    
    # Compute inv^k using cycle decomposition
    # Each element x maps to: apply inv k times starting from x
    result = [0] * (n + 1)
    visited = [False] * (n + 1)
    
    for start in range(1, n + 1):
        if visited[start]:
            continue
        
        # Build cycle starting from 'start'
        cycle = []
        current = start
        while not visited[current]:
            visited[current] = True
            cycle.append(current)
            current = inv[current]
        
        # Apply k steps in cycle
        cycle_len = len(cycle)
        for i in range(cycle_len):
            new_idx = (i + k) % cycle_len
            result[cycle[i]] = cycle[new_idx]
    
    # Convert to 0-indexed output format
    output = [result[i + 1] for i in range(n)]
    print(str(output).replace(' ', ''))

if __name__ == "__main__":
    main()
