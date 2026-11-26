import sys

def main():
    data = sys.stdin.read().split()
    if not data:
        return
    R = int(data[0])
    
    lines = []
    for i in range(R):
        row = []
        for j in range(R):
            dist = max(abs(i - R // 2), abs(j - R // 2))
            row.append(str(dist + 1))
        lines.append(''.join(row))
    
    print('\n'.join(lines))

if __name__ == '__main__':
    main()
