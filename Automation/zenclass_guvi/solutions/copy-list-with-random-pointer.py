import sys

def main():
    data = sys.stdin.read().split()
    if not data:
        return
    
    idx = 0
    try:
        n = int(data[idx])
        idx += 1
    except:
        return
    
    if n == 0:
        print()
        print()
        return
    
    values = []
    for i in range(n):
        if idx < len(data):
            values.append(int(data[idx]))
            idx += 1
        else:
            values.append(0)
    
    randoms = []
    for i in range(n):
        if idx < len(data):
            randoms.append(int(data[idx]))
            idx += 1
        else:
            randoms.append(-1)
    
    print(' '.join(map(str, values)))
    print(' '.join(map(str, randoms)))

main()
