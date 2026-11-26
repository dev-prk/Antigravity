import sys

def main():
    data = sys.stdin.read().splitlines()
    if not data:
        return
    n = int(data[0].strip())
    if n == 0:
        return
    strings = []
    for i in range(1, n + 1):
        if i < len(data):
            strings.append(data[i])
        else:
            strings.append("")
    
    strings.sort()
    
    for s in strings:
        print(s)

if __name__ == "__main__":
    main()
