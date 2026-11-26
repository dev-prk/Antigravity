import sys

def main():
    line = sys.stdin.readline().strip()
    if '=' in line:
        mask = int(line.split('=')[1])
    else:
        mask = int(line)
    
    submasks = []
    s = mask
    while True:
        submasks.append(s)
        if s == 0:
            break
        s = (s - 1) & mask
    
    print(f"[{','.join(map(str, submasks))}]")

if __name__ == "__main__":
    main()
