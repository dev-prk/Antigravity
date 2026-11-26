import sys

def main():
    data = sys.stdin.read().splitlines()
    if not data:
        return
    
    parts = data[0].split()
    n = int(parts[0])
    
    if n == 0:
        return
    
    list1 = list(map(int, data[1].split()))
    list2 = list(map(int, data[2].split()))
    
    for i in range(n):
        print(f"{list1[i]} {list2[n - 1 - i]}")

if __name__ == "__main__":
    main()
