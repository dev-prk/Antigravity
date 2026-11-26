import sys

def solve():
    data = sys.stdin.read().strip().split()
    if not data:
        return
    N = int(data[0])
    M = int(data[1])
    
    if N > M + 1:
        print(-1)
        return
    
    if N == 0:
        print('1' * M)
        return
    
    result = []
    zeros = N
    ones = M
    
    consecutive_ones = 0
    last_is_zero = False
    
    while zeros > 0 or ones > 0:
        placed = False
        
        if zeros > 0 and not last_is_zero:
            result.append('0')
            zeros -= 1
            consecutive_ones = 0
            last_is_zero = True
            placed = True
        elif ones > 0 and consecutive_ones < 2:
            result.append('1')
            ones -= 1
            consecutive_ones += 1
            last_is_zero = False
            placed = True
        
        if not placed:
            print(-1)
            return
    
    print(''.join(result))

solve()
