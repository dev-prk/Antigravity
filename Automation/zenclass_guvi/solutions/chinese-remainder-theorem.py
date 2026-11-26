import sys
import math

def extended_gcd(a, b):
    if a == 0:
        return b, 0, 1
    gcd, x1, y1 = extended_gcd(b % a, a)
    x = y1 - (b // a) * x1
    y = x1
    return gcd, x, y

def mod_inverse(a, m):
    gcd, x, _ = extended_gcd(a, m)
    if gcd != 1:
        return -1
    return (x % m + m) % m

def chinese_remainder_theorem(r, m):
    if len(r) == 0:
        return 0
    
    M = 1
    for mi in m:
        if mi <= 0:
            return -1
        M *= mi
    
    x = 0
    for i in range(len(r)):
        ri, mi = r[i], m[i]
        Mi = M // mi
        yi = mod_inverse(Mi, mi)
        if yi == -1:
            return -1
        x += ri * Mi * yi
    
    return x % M

def main():
    line = sys.stdin.readline().strip()
    if not line:
        print(0)
        return
    
    r = []
    m = []
    
    if line.startswith('r='):
        r_start = line.find('[')
        r_end = line.find(']')
        r_part = line[r_start+1:r_end]
        r = list(map(int, r_part.split(',')))
        
        m_start = line.find('m=')
        if m_start != -1:
            m_section = line[m_start+2:]
            m_start_bracket = m_section.find('[')
            m_end_bracket = m_section.find(']')
            m_part = m_section[m_start_bracket+1:m_end_bracket]
            m = list(map(int, m_part.split(',')))
    else:
        parts = line.split()
        for p in parts:
            if p.startswith('r='):
                r_part = p[2:].strip('[]')
                r = list(map(int, r_part.split(',')))
            elif p.startswith('m='):
                m_part = p[2:].strip('[]')
                m = list(map(int, m_part.split(',')))
    
    result = chinese_remainder_theorem(r, m)
    print(result)

if __name__ == "__main__":
    main()
