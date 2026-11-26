import sys

def is_jolly(seq):
    n = len(seq)
    if n == 1:
        return True
    
    diffs = set()
    for i in range(n - 1):
        diff = abs(seq[i + 1] - seq[i])
        if diff < 1 or diff >= n:
            return False
        if diff in diffs:
            return False
        diffs.add(diff)
    
    return len(diffs) == n - 1

for line in sys.stdin:
    line = line.strip()
    if not line:
        continue
    
    parts = line.split()
    n = int(parts[0])
    
    if n == 0 or n >= 3000:
        print("Not jolly")
        continue
    
    if len(parts) - 1 != n:
        print("Not jolly")
        continue
    
    try:
        seq = [int(x) for x in parts[1:]]
    except:
        print("Not jolly")
        continue
    
    if is_jolly(seq):
        print("Jolly")
    else:
        print("Not jolly")
