import sys

def main():
    data = sys.stdin.read().strip().split()
    if len(data) < 3:
        print('no')
        return
    
    try:
        A = float(data[0])
        B = float(data[1])
        C = float(data[2])
    except (ValueError, IndexError):
        print('no')
        return
    
    if A <= 0 or B <= 0 or C <= 0:
        print('no')
        return
    
    sides = sorted([A, B, C])
    
    if sides[0] + sides[1] > sides[2]:
        print('yes')
    else:
        print('no')

if __name__ == "__main__":
    main()
