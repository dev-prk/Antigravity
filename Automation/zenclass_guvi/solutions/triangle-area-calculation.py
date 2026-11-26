import sys

def main():
    data = sys.stdin.read().strip().split()
    if len(data) < 2:
        return
    B = int(data[0])
    H = int(data[1])
    area = (B * H) // 2
    print(area)

if __name__ == "__main__":
    main()
