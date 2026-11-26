import sys

def main():
    data = sys.stdin.read().strip().split()
    if not data:
        return
    
    m = int(data[0])
    n = int(data[1])
    
    if m == 0 or n == 0:
        for _ in range(m):
            print()
        return
    
    elements = list(map(int, data[2:2 + m * n]))
    elements.sort()
    
    result = []
    for i in range(m):
        row = elements[i * n:(i + 1) * n]
        result.append(' '.join(map(str, row)))
    
    print('\n'.join(result))

if __name__ == "__main__":
    main()
