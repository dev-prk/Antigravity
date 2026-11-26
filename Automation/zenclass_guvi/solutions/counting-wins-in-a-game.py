import sys

def main():
    data = sys.stdin.read().strip().split()
    if not data:
        print("RAM: 0")
        print("SITA: 0")
        return
    
    m = int(data[0])
    n = int(data[1])
    
    zero_count = 0
    index = 2
    for _ in range(m):
        for _ in range(n):
            if index < len(data):
                val = int(data[index])
                index += 1
                if val == 0:
                    zero_count += 1
    
    total = m * n
    one_count = total - zero_count
    
    print(f"RAM: {zero_count}")
    print(f"SITA: {one_count}")

if __name__ == "__main__":
    main()
