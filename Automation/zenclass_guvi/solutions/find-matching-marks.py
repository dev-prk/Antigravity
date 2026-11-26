import sys

def main():
    data = sys.stdin.read().strip().split()
    if not data:
        print(-1)
        return
    
    n = int(data[0])
    ramesh_mark = int(data[1])
    
    if n == 0 or len(data) < 2 + n:
        print(-1)
        return
    
    marks = list(map(int, data[2:2+n]))
    
    found = False
    for i in range(len(marks)):
        if marks[i] == ramesh_mark:
            print(i)
            found = True
            break
    
    if not found:
        print(-1)

if __name__ == "__main__":
    main()
