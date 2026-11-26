import sys

def main():
    lines = sys.stdin.read().splitlines()
    if len(lines) < 2:
        print(-1)
        return
    
    S = lines[0].strip()
    X = lines[1].strip()
    
    words = S.split()
    
    for i in range(len(words)):
        if words[i] == X:
            print(i + 1)
            return
    
    print(-1)

if __name__ == "__main__":
    main()
