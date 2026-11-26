import sys

def main():
    data = sys.stdin.read().strip().split()
    if not data:
        return
    n = int(data[0])
    elements = data[1:n+1]
    reversed_elements = elements[::-1]
    print(' '.join(reversed_elements))

if __name__ == "__main__":
    main()
