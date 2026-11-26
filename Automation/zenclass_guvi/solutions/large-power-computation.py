import sys

def main():
    line = sys.stdin.readline().strip()
    if not line:
        return
    
    parts = line.split(',')
    n_part = parts[0].strip()
    m_part = parts[1].strip()
    
    n = int(n_part.split('=')[1])
    m = int(m_part.split('=')[1])
    
    result = pow(2, n, m)
    print(result)

if __name__ == "__main__":
    main()
