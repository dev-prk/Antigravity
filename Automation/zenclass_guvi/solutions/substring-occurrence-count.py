import sys

def main():
    data = sys.stdin.read().splitlines()
    if not data:
        return
    parent = data[0]
    pattern = data[1] if len(data) > 1 else ''
    if pattern == '':
        print(0)
        return
    count = 0
    idx = 0
    while True:
        idx = parent.find(pattern, idx)
        if idx == -1:
            break
        count += 1
        idx += 1  # allow overlapping
    print(count)

if __name__ == "__main__":
    main()
