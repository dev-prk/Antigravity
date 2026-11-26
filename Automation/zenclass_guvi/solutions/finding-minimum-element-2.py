import sys

def main():
    data = sys.stdin.read().strip().split()
    if not data:
        print(-1)
        return
    n = int(data[0])
    if n == 0:
        print(-1)
        return
    elements = list(map(int, data[1:n+1]))
    if not elements:
        print(-1)
        return
    min_element = elements[0]
    for i in range(1, len(elements)):
        if elements[i] < min_element:
            min_element = elements[i]
    print(min_element)

if __name__ == "__main__":
    main()
