import sys

def main():
    data = sys.stdin.read().split()
    n = int(data[0])
    k = int(data[1])
    p = int(data[2])
    a = list(map(int, data[3:3+n]))
    b = list(map(int, data[3+n:3+n+k]))
    
    a.sort()
    b.sort()
    
    min_time = float('inf')
    
    for start in range(k - n + 1):
        current_max = 0
        for i in range(n):
            key_pos = b[start + i]
            time_a = abs(a[i] - key_pos)
            time_b = abs(key_pos - p)
            time_total = time_a + time_b
            if time_total > current_max:
                current_max = time_total
        if current_max < min_time:
            min_time = current_max
    
    print(min_time)

if __name__ == "__main__":
    main()
