import sys

def main():
    line = sys.stdin.readline().strip()
    if '=' in line:
        n = int(line.split('=')[1])
    else:
        n = int(line)
    
    if n == 0:
        print('[]')
        return
    
    result = []
    for mask in range(1 << n):
        s = 0
        for i in range(n):
            if mask & (1 << i):
                s += 1 << i
        result.append(s)
    
    print('[' + ','.join(map(str, result)) + ']')

if __name__ == "__main__":
    main()
