import sys

def main():
    line = sys.stdin.readline().strip()
    if not line:
        return
    idx = line.find('=')
    if idx == -1:
        return
    g = int(line[idx+1:])
    res = 0
    while g > 0:
        res ^= g
        g >>= 1
    print(res)

if __name__ == "__main__":
    main()
