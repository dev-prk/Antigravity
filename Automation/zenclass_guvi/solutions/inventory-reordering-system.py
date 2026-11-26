import sys

def main():
    data = sys.stdin.read().strip().split('\n')
    if not data:
        return
    
    try:
        n = int(data[0].strip())
    except:
        n = 0
    
    items = []
    for i in range(1, n + 1):
        if i < len(data):
            line = data[i].strip()
            if ',' in line:
                name_part, stock_part = line.rsplit(',', 1)
                name = name_part.strip()
                stock = int(stock_part.strip())
                items.append((name, stock))
            else:
                continue
    
    items.sort(key=lambda x: x[1])
    
    critical = []
    for name, stock in items:
        if stock < 10:
            critical.append(name)
    
    for name, stock in items:
        print(f"{name},{stock}")
    
    if critical:
        print(','.join(critical))
    else:
        print()

if __name__ == '__main__':
    main()
