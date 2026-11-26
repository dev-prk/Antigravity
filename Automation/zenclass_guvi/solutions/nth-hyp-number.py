import sys
from itertools import product

def solve():
    data = sys.stdin.read().strip()
    if not data:
        return
    n = int(data)
    primes = [2, 3, 5, 7]
    
    # Generate hyp numbers in increasing order
    # 1-digit, 2-digit, 3-digit, etc.
    count = 0
    ans = None
    
    # For numbers with d digits, the first digit can be 2,3,5,7
    # and the rest can be 2,3,5,7
    # We need to iterate in order: all 1-digit, then all 2-digit (in lex order = numeric order), etc.
    
    d = 1
    while ans is None:
        # Generate all d-digit hyp numbers in sorted order
        # First digit: 2,3,5,7
        # Remaining d-1 digits: 2,3,5,7
        for first in primes:
            if count < n:
                # Need to generate (d-1) suffixes in lex order
                for suffix in product(primes, repeat=d-1):
                    num_str = str(first) + ''.join(str(x) for x in suffix)
                    count += 1
                    if count == n:
                        ans = num_str
                        break
                if ans is not None:
                    break
        d += 1
    
    print(ans)

solve()
