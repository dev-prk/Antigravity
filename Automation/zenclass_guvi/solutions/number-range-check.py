import sys

def main():
    data = sys.stdin.read().strip().split()
    if len(data) < 3:
        print('no')
        return
    
    N = int(data[0])
    L = int(data[1])
    R = int(data[2])
    
    if L <= R:
        if L <= N <= R:
            print('yes')
        else:
            print('no')
    else:
        if R <= N <= L:
            print('yes')
        else:
            print('no')

if __name__ == "__main__":
    main()
