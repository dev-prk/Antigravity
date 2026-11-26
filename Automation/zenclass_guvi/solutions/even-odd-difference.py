import sys

def main():
    line = sys.stdin.readline()
    if not line:
        return
    parts = line.strip().split()
    if len(parts) < 2:
        return
    try:
        N = int(parts[0])
        M = int(parts[1])
    except ValueError:
        return
    
    diff = abs(N - M)
    if diff % 2 == 0:
        print("even")
    else:
        print("odd")

if __name__ == "__main__":
    main()
