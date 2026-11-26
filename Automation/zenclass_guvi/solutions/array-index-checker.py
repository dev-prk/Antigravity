import sys

def main():
    try:
        n = int(sys.stdin.readline().strip())
        arr = []
        for _ in range(n):
            arr.append(int(sys.stdin.readline().strip()))
        index = int(sys.stdin.readline().strip())
        if index < 0 or index >= n:
            raise IndexError
        print(arr[index])
    except (IndexError, Exception):
        print("Error: Index out of bounds")

if __name__ == "__main__":
    main()
