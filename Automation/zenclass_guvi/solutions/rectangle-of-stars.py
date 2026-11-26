import sys

def main():
    data = sys.stdin.read().strip().split()
    if not data:
        return
    R = int(data[0])
    C = int(data[1])
    
    for i in range(R):
        print(' '.join(['*'] * C))

if __name__ == "__main__":
    main()
