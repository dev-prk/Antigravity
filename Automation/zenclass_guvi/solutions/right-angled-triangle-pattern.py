import sys

def main():
    data = sys.stdin.read().strip()
    if not data:
        return
    try:
        N = int(data)
    except ValueError:
        return
    
    if N <= 0:
        return
    
    count = 1
    for i in range(N):
        print(' '.join(['1'] * count))
        count += 2

if __name__ == "__main__":
    main()
