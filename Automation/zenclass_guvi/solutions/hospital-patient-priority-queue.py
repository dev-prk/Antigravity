import sys

def main():
    data = sys.stdin.read().split()
    if not data:
        return
    n = int(data[0])
    if n == 0:
        return
    priorities = list(map(int, data[1:1 + n]))
    if not priorities:
        return
    print(f"Patient Priority: {min(priorities)}")

if __name__ == "__main__":
    main()
