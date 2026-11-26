import sys

def main():
    data = sys.stdin.read().strip().split()
    if not data:
        print("Total Connections: 0")
        return
    
    n = int(data[0])
    e = int(data[1])
    
    print(f"Total Connections: {e}")

if __name__ == "__main__":
    main()
