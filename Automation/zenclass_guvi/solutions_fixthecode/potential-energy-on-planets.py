import sys
import math

def main():
    data = sys.stdin.read().strip().split()
    if not data:
        return
    
    idx = 0
    n = int(data[idx]); idx += 1
    d = {}
    for _ in range(n):
        planet = data[idx]; idx += 1
        g = float(data[idx]); idx += 1
        d[planet] = g
    
    q = int(data[idx]); idx += 1
    out = []
    for _ in range(q):
        u = float(data[idx]); idx += 1
        planet = data[idx]; idx += 1
        h = float(data[idx]); idx += 1
        g = d[planet]
        if g == 0 or h == 0:
            out.append("0.00")
        else:
            m = u / (g * h)
            # Round to 2 decimal places with special handling for exact halfway cases
            m_rounded = round(m + 1e-9, 2)
            out.append("%.2f" % m_rounded)
    
    sys.stdout.write("\n".join(out))

main()
