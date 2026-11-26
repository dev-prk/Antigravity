import sys

def main():
    R = int(sys.stdin.readline().strip())
    
    for i in range(1, R + 1):
        if i == 1:
            print("1")
        elif i == R:
            print(''.join(str(j) for j in range(1, i + 1)))
        else:
            row = ['1'] + [' ' * (i - 2)] + [str(i)]
            print(''.join(row))

if __name__ == "__main__":
    main()
