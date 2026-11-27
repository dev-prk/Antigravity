import sys
from fractions import Fraction

def solve():
    data = sys.stdin.read().strip().split()
    if not data:
        return
    n = int(data[0])
    a = list(map(int, data[1:1+n]))
    
    if n < 4:
        for x in a:
            print(x, end=' ')
        return
    
    candidates = set()
    
    if a[0] != 0 and a[2] != 0:
        r = Fraction(a[2], a[0])
        if r.denominator == 1:
            candidates.add(int(r))
    
    if a[1] != 0 and a[3] != 0:
        r = Fraction(a[3], a[1])
        if r.denominator == 1:
            candidates.add(int(r))
    
    candidates.add(1)
    
    if a[0] != 0:
        max_r = 100
        for r in range(-max_r, max_r + 1):
            if r == 0:
                continue
            candidates.add(r)
    
    candidates.add(0)
    
    def check_and_fix(arr, r):
        if r == 0:
            return None
        fixed = []
        for i in range(len(arr)):
            if arr[0] * (r ** i) == arr[i]:
                fixed.append(arr[i])
            else:
                if len(fixed) < i and arr[0] * (r ** i) == arr[i]:
                    fixed.append(arr[i])
                elif len(fixed) >= i and len(fixed) < len(arr):
                    candidate = arr[0] * (r ** i)
                    if len(fixed) == i:
                        fixed.append(candidate)
                    elif fixed[i] != candidate:
                        return None
                else:
                    return None
        
        changes = 0
        for i in range(len(arr)):
            expected = arr[0] * (r ** i)
            if arr[i] != expected:
                changes += 1
                if changes > 1:
                    return None
        
        if changes <= 1:
            return [arr[0] * (r ** i) for i in range(len(arr))]
        return None
    
    def is_gp(arr):
        if len(arr) <= 1:
            return True
        if arr[0] == 0:
            return all(x == 0 for x in arr[1:])
        r = Fraction(arr[1], arr[0])
        for i in range(2, len(arr)):
            if arr[i-1] == 0:
                if arr[i] != 0:
                    return False
            else:
                if Fraction(arr[i], arr[i-1]) != r:
                    return False
        return True
    
    result = None
    
    for r in candidates:
        fixed = check_and_fix(a, r)
        if fixed is not None:
            if is_gp(fixed):
                result = fixed
                break
    
    if result is None:
        for i in range(n):
            for j in range(-100, 101):
                original = a[i]
                a[i] = j
                if is_gp(a):
                    result = a[:]
                    a[i] = original
                    if result is not None:
                        break
                a[i] = original
            if result is not None:
                break
    
    if result is None:
        if is_gp(a):
            result = a[:]
        else:
            print(-1)
            return
    
    print(' '.join(map(str, result)))

solve()
