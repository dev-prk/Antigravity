import sys

def main():
    data = sys.stdin.read().strip().split()
    if len(data) < 3:
        print('no')
        return
    
    try:
        A = int(data[0])
        B = int(data[1])
        C = int(data[2])
    except:
        print('no')
        return
    
    if A + B + C == 180 and A > 0 and B > 0 and C > 0:
        print('yes')
    else:
        print('no')

if __name__ == "__main__":
    main()
