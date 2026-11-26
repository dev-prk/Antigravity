import sys

def main():
    data = sys.stdin.read().strip().split('\n')
    if not data:
        return
    
    n = int(data[0].strip())
    
    if n == 0:
        return
    
    max_avg = float('-inf')
    result_name = ""
    
    for i in range(1, n + 1):
        if i >= len(data):
            break
        line = data[i].strip()
        if not line:
            continue
        parts = line.split()
        name = parts[0]
        m1 = int(parts[1])
        m2 = int(parts[2])
        m3 = int(parts[3])
        
        avg = (m1 + m2 + m3) / 3.0
        
        if avg > max_avg:
            max_avg = avg
            result_name = name
    
    print(result_name)

if __name__ == "__main__":
    main()
