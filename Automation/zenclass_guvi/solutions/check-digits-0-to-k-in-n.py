def main():
    import sys
    data = sys.stdin.read().split()
    n = data[0]
    k = int(data[1])
    
    present = [False] * 10
    for c in n:
        d = int(c)
        present[d] = True
    
    for i in range(k + 1):
        if i >= 10:
            print("no")
            return
        if not present[i]:
            print("no")
            return
    
    print("yes")

if __name__ == "__main__":
    main()
