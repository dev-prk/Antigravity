import sys

# Precompute factorials for digits 0-9
fact = [1, 1, 2, 6, 24, 120, 720, 5040, 40320, 362880]

def solve():
    n = int(sys.stdin.readline().strip())
    
    if n == 0:
        print(-1)
        return
    
    # Greedy approach: use largest digits first to minimize count
    result = []
    
    while n > 0:
        found = False
        for d in range(9, -1, -1):
            if n >= fact[d]:
                n -= fact[d]
                result.append(d)
                found = True
                break
        
        if not found:
            print(-1)
            return
    
    # Sort digits in ascending order to get smallest number
    result.sort()
    
    # Remove leading zeros (but keep at least one digit)
    if result[0] == 0:
        # Find first non-zero digit and swap
        i = 0
        while i < len(result) and result[i] == 0:
            i += 1
        if i < len(result):
            result[0], result[i] = result[i], result[0]
        else:
            print(-1)
            return
    
    print(''.join(map(str, result)))

if __name__ == "__main__":
    solve()
