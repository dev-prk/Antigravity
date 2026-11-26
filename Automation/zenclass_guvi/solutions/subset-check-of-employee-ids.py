import sys

def main():
    data = sys.stdin.read().strip().split()
    if not data:
        print("yes")
        return
    
    idx = 0
    n1 = int(data[idx])
    idx += 1
    project1 = list(map(int, data[idx:idx + n1]))
    idx += n1
    n2 = int(data[idx])
    idx += 1
    project2 = list(map(int, data[idx:idx + n2]))
    
    set1 = set(project1)
    set2 = set(project2)
    
    if set2.issubset(set1):
        print("yes")
    else:
        print("no")

if __name__ == "__main__":
    main()
